import torch
import torch.nn as nn
from torchvision.models.resnet import resnet50, ResNet50_Weights
import torch.nn.functional as F

def _adaptar_conv1(encoder, input_channels):
    """
    Adapta a primeira convolução (conv1) para len(input_channels) canais,
    reaproveitando os pesos pré-treinados no ImageNet:
      - r, g, b -> pesos pré-treinados R, G, B
      - n (NIR) -> duplica o peso do canal Red (estratégia do paper p/ NRGB)
      - v (NDVI), w (NDWI) -> zeros (índices derivados; a rede aprende do zero)
    Para input_channels='rgb' reproduz exatamente o conv1 original.
    """
    conv1 = encoder.conv1
    peso_pretrained = conv1.weight.data            # [64, 3, 7, 7], ordem R, G, B
    out_ch, _, kh, kw = peso_pretrained.shape
    C = len(input_channels)

    fonte = {'r': 0, 'g': 1, 'b': 2, 'n': 0}       # n copia o Red; v/w ficam zero
    novo_peso = torch.zeros(out_ch, C, kh, kw)
    for i, c in enumerate(input_channels):
        if c in fonte:
            novo_peso[:, i] = peso_pretrained[:, fonte[c]]

    nova_conv1 = nn.Conv2d(C, out_ch, kernel_size=conv1.kernel_size,
                           stride=conv1.stride, padding=conv1.padding, bias=False)
    nova_conv1.weight.data = novo_peso
    encoder.conv1 = nova_conv1


def get_fpn_resnet_encoder(input_channels='rgb'):
    encoder = resnet50(
        weights='DEFAULT',
        replace_stride_with_dilation=[False, False, True]
    )

    for m in encoder.layer4.modules():
        if isinstance(m, nn.Conv2d) and m.kernel_size == (3, 3):
            m.dilation = (4, 4)
            m.padding = (4, 4)  # padding de 4 também pra não encolher a imagem

    _adaptar_conv1(encoder, input_channels)

    if hasattr(encoder, 'fc'):
        del encoder.fc
    if hasattr(encoder, 'avgpool'):
        del encoder.avgpool

    return encoder

class LateralConnection(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        # Usamos padding=1 no kernel=3 para não encolher a imagem
        self.block = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.LeakyReLU(negative_slope=0.01, inplace=True),
            
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.LeakyReLU(negative_slope=0.01, inplace=True),
            
            nn.Conv2d(out_channels, out_channels, kernel_size=1, bias=False)
        )

    def forward(self, x):
        return self.block(x)


class UpsamplingModule(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.block = nn.Sequential(
            # O PULO DO GATO: Para que um kernel=3, stride=2 e padding=1 dobre o tamanho
            # da imagem exatemente (ex: 56x56 -> 112x112), o PyTorch EXIGE o output_padding=1.
            # Os papers quase nunca citam isso pois é uma peculiaridade do framework.
            nn.ConvTranspose2d(in_channels, out_channels, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.BatchNorm2d(out_channels),
            nn.LeakyReLU(negative_slope=0.01, inplace=True),
            
            nn.Conv2d(out_channels, out_channels, kernel_size=1, bias=False)
        )

    def forward(self, x):
        return self.block(x)


class PostFusionModule(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(channels),
            nn.LeakyReLU(negative_slope=0.01, inplace=True),
            
            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(channels),
            nn.LeakyReLU(negative_slope=0.01, inplace=True)
        )

    def forward(self, x):
        return self.block(x)

class FPNDecoder(nn.Module):
    def __init__(self, encoder_channels, fpn_channels, num_classes):
        """
        encoder_channels: lista com a quantidade de canais que saem de cada nível da ResNet
                          (ex: [256, 512, 1024, 2048] para layer1, 2, 3 e 4)
        fpn_channels: quantidade de canais padronizada dentro do decoder (ex: 256)
        """
        super().__init__()
        
        self.laterals = nn.ModuleList([
            LateralConnection(in_channels=c, out_channels=fpn_channels) 
            for c in encoder_channels
        ])
        
        # Criando os módulos de upsample (serão 1 a menos que o total de níveis, 
        # pois o nível mais baixo não recebe upsample de ninguém)
        self.upsamples = nn.ModuleList([
            UpsamplingModule(in_channels=fpn_channels, out_channels=fpn_channels)
            for _ in range(len(encoder_channels) - 2)
        ])
        
        self.post_fusions = nn.ModuleList([
            PostFusionModule(channels=fpn_channels)
            for _ in range(len(encoder_channels) - 1)
        ])

        total_concat_channels = fpn_channels * len(encoder_channels)
        self.final_conv = nn.Conv2d(total_concat_channels, num_classes, kernel_size=1, bias=True)

    def forward(self, encoder_features):
        # encoder_features é uma lista de tensores [C2, C3, C4, C5] vindo da ResNet
        
        # Passam-se todas as features pelas conexões laterais
        # Isso padroniza todos os níveis para terem a mesma quantidade de canais (ex: 256)
        lat_features = [lateral(f) for lateral, f in zip(self.laterals, encoder_features)]
        
        # Caminho Top-Down (De cima para baixo, somando e fazendo Post-Fusion)
        # Começamos do nível mais alto (com menor resolução, ex: layer4 da ResNet)
        outs = [lat_features[-1]]
        
        for i in range(len(lat_features) - 2, -1, -1):
            if i < 2:
                upsampled_top = self.upsamples[i](outs[-1])
                added = lat_features[i] + upsampled_top
            else:
                added = lat_features[i] + outs[-1]           
            fused = self.post_fusions[i](added)
            
            outs.append(fused)
            
        resolution = outs[-1].shape[2:] 
        
        upsampled_outs = []
        for out in outs:
            # "outputs from all pyramid levels are upsampled to the highest pyramid resolution 
            # using bilinear interpolation"
            up = F.interpolate(out, size=resolution, mode='bilinear', align_corners=False)
            upsampled_outs.append(up)
            
        concat_features = torch.cat(upsampled_outs, dim=1)
        
        semantic_map = self.final_conv(concat_features)
        
        return semantic_map

class FPN_ResNet50_Segmentation(nn.Module):
    def __init__(self, num_classes=9, input_mean=None, input_std=None, input_channels='rgb'):
        super().__init__()

        self.encoder = get_fpn_resnet_encoder(input_channels=input_channels)

        
        encoder_channels = [256, 512, 1024, 2048]


        # O paper FPN geralmente usa 256 canais internos para as conexões laterais
        self.decoder = FPNDecoder(
            encoder_channels=encoder_channels,
            fpn_channels=256,
            num_classes=num_classes
        )

        if input_mean is None:
            input_mean, input_std = torch.zeros(3), torch.ones(3)
        input_mean = torch.as_tensor(input_mean, dtype=torch.float32).view(1, -1, 1, 1)
        input_std  = torch.as_tensor(input_std,  dtype=torch.float32).view(1, -1, 1, 1)
        self.register_buffer("input_mean", input_mean)
        self.register_buffer("input_std",  input_std)

    def forward(self, x):
        # Normaliza a entrada usando as estatísticas do dataset
        x = (x - self.input_mean) / (self.input_std)

        tamanho_original = (x.shape[2], x.shape[3])
        
        # Encoder
        x = self.encoder.conv1(x)
        x = self.encoder.bn1(x)
        x = self.encoder.relu(x)
        x = self.encoder.maxpool(x)

        c2 = self.encoder.layer1(x)  
        c3 = self.encoder.layer2(c2)  
        c4 = self.encoder.layer3(c3)  
        c5 = self.encoder.layer4(c4)  
        
        # Decoder
        features = [c2, c3, c4, c5]
        
        # O mapa semântico sai daqui com tamanho reduzido (ex: 128x128)
        semantic_map = self.decoder(features)
        
        # No paper não foi encontrado a especificação da interpolação, mas era 
        # preciso para ficar do mesmo tamanho da imagem de entrada.
        return F.interpolate(
            semantic_map, 
            size=tamanho_original, 
            mode='bilinear', 
            align_corners=False
        )
