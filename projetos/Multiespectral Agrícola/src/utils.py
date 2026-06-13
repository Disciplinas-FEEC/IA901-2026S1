import pickle
import random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import torch
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
from PIL import Image
from tqdm import tqdm
import yaml
import matplotlib
from .constants import CLASSES_DICT, BAND_DICT

# _CONFIG_PATH = "../config.yaml"


def _render_plots_data(secao: str, plots_data: list, sample_id: str = "") -> None:
    n_cols = len(plots_data)
    fig, axes = plt.subplots(1, n_cols, figsize=(4 * n_cols, 4), squeeze=False)
    fig.suptitle(f"[{secao}]  ID: {sample_id}", fontsize=13, fontweight="bold")
    for col, (titulo, data, cmap, vmin, vmax, has_colorbar) in enumerate(plots_data):
        ax = axes[0][col]
        im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
        ax.set_title(titulo, fontsize=10)
        ax.set(xticks=[], yticks=[])
        for spine in ax.spines.values():
            spine.set(edgecolor="black", linewidth=0.8)
        if has_colorbar:
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    plt.tight_layout()
    plt.show()


def _build_rgb(image_np: np.ndarray, input_channels: str) -> np.ndarray:
    idx = {c: i for i, c in enumerate(input_channels)}
    H, W = image_np.shape[1], image_np.shape[2]
    rgb = np.stack([
        image_np[idx[c]].numpy() 
        if c in idx 
        else np.zeros((H, W),dtype=np.float32)
        for c in ('r', 'g', 'b')
    ], axis=-1)
    return rgb


def printInput(image: torch.Tensor, input_channels: str, mask: torch.Tensor, id: str) -> None:
    idx   = {c: i for i, c in enumerate(input_channels)}
    rgb   = _build_rgb(image, input_channels)

    H, W = image.shape[1], image.shape[2]

    facecolor = 'black'
    # Linha 0: RGB composto + canais R, G, B com Reds/Greens/Blues, inválidos em preto
    row0 = [("RGB", rgb, None, None, None, False, facecolor)]
    for letra in ('r', 'g', 'b'):
        if letra in idx:
            canal = image[idx[letra]].numpy().copy()
            canal[(mask.numpy() == 0)] = np.nan
            row0.append((BAND_DICT[letra]['name'], canal,
                        BAND_DICT[letra]['cmap'],
                        BAND_DICT[letra]['vmin'],
                        BAND_DICT[letra]['vmax'],
                        BAND_DICT[letra]['colorbar'],
                        facecolor))

    # Linha 1: NIR, NDVI, NDWI
    row1 = []
    for letra in ('n', 'v', 'w'):
        if letra in idx:
            canal = image[idx[letra]].numpy().copy()
            if letra in ('v', 'w'):
                canal[(mask.numpy() == 0)] = np.nan
            row1.append((BAND_DICT[letra]['name'],
                         canal,
                         BAND_DICT[letra]['cmap'],
                         BAND_DICT[letra]['vmin'],
                         BAND_DICT[letra]['vmax'],
                         BAND_DICT[letra]['colorbar'],
                         facecolor))


    n_cols = max(len(row0), len(row1))
    n_rows = 2 if row1 else 1

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 4 * n_rows), squeeze=False)
    fig.suptitle(f"[INPUT]  ID: {id}", fontsize=13, fontweight="bold")

    for row_idx, plots_data in enumerate([row0, row1] if row1 else [row0]):
        for col in range(n_cols):
            ax = axes[row_idx][col]
            if col < len(plots_data):
                panel = plots_data[col]
                title, img, cmap, vmin, vmax, has_colorbar = panel[:6]
                facecolor = panel[6] if len(panel) > 6 else 'white'
                ax.set_facecolor(panel[6])
                im = ax.imshow(img, cmap=cmap, vmin=vmin, vmax=vmax)
                ax.set_title(title, fontsize=10)
                ax.set(xticks=[], yticks=[])
                for spine in ax.spines.values():
                    spine.set(edgecolor="black", linewidth=0.8)
                if has_colorbar:
                    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            else:
                ax.axis("off")

    plt.tight_layout()
    plt.show()


def printOutput(image: torch.Tensor,
                input_channels: str,
                classes2eval: list,
                labels: torch.Tensor,
                mask: torch.Tensor,
                id: str) -> None:

    labels_np = labels.numpy()
    idx_band = {c: i for i, c in enumerate(input_channels)}

    K, H, W = labels_np.shape
    rgb   = _build_rgb(image, input_channels)
    ALPHA = 0.5

    class_masks = []
    for k, class_name in enumerate(classes2eval):
        class_color = np.array(CLASSES_DICT.get(class_name)['color'], dtype=np.float32)
        mascara     = labels_np[k] > 0
        if mascara.sum() == 0:
            continue
        class_masks.append((class_name, class_color, mascara))

    def _masks_overlay_img(base):
        img = base.copy()
        for _, class_color, mascara in class_masks:
            img[mascara] = (1 - ALPHA) * base[mascara] + ALPHA * class_color
        return img

    # Faz a representação visual de um único valor escalar por pixel.
    def _to_rgb(canal, cmap_name, vmin, vmax, apply_roi=False):
        arr = canal.copy().astype(np.float32)
        if apply_roi:
            arr[mask.numpy() == 0] = np.nan
        colored = plt.get_cmap(cmap_name)(plt.Normalize(vmin=vmin, vmax=vmax)(arr))[:, :, :3].astype(np.float32)
        # if apply_roi and roi is not None:
        #     colored[~roi] = 0.0
        return colored

    overlays = [("RGB + Labels", _masks_overlay_img(rgb), None, None, None, False)]
    for letra, label in [('n', 'NIR'), ('v', 'NDVI'), ('w', 'NDWI')]:
        if letra in idx_band:
            base_rgb = _to_rgb(image[idx_band[letra]].numpy(),
                               BAND_DICT[letra]['cmap'],
                               BAND_DICT[letra]['vmin'],
                               BAND_DICT[letra]['vmax'],
                                apply_roi=(letra in ('v', 'w')))
            overlays.append((f"{label} + Labels", _masks_overlay_img(base_rgb), None, None, None, False))

    panels = []
    for class_name, class_color, mascara in class_masks:
        rgba = np.ones((H, W, 4), dtype=np.float32)
        rgba[mascara, :3] = class_color
        panels.append((class_name, rgba, None, None, None, False))

    _render_plots_data("OUTPUT — Overlays", overlays, id)
    _render_plots_data("OUTPUT — Classes",  panels,   id)


def printContext(mask: torch.Tensor,
                 boundary: torch.Tensor,
                 image:torch.Tensor,
                 input_channels: str,
                 id: str) -> None:
    mask_np = mask.numpy()
    boundary_np = boundary.numpy()
    rgb = _build_rgb(image, input_channels)

    plot_data = []
    plot_data.append(("Mask", mask_np, "gray", 0, 1, False))
    plot_data.append(("Boundary", boundary_np, "gray", 0, 1, False))
    roi     = np.expand_dims((mask_np > 0) & (boundary_np > 0), axis=-1)
    rgb_roi = np.where(roi, rgb, 0).astype(np.float32)
    plot_data.append(("ROI (RGB)", rgb_roi, None, None, None, False))

    _render_plots_data("Region of Interest (ROI)", plot_data, id)


def printSample(sample: dict) -> None:
    printInput(sample)
    printOutput(sample)
    printContext(sample)


def printSampleById(path: str) -> None:
    path = Path(path)
    img = Image.open(path)
    plt.imshow(img)
    plt.title(path.stem, fontsize=11)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def printColorPalette() -> None:
    ID_TO_CLASS = {info['id']: name for name, info in CLASSES_DICT.items()}
    items = sorted(CLASSES_DICT.values(), key=lambda x: x['id'])
    n = len(items)

    fig, axes = plt.subplots(1, n, figsize=(n * 1.4, 1.8))
    for item, ax in zip(items, axes):
        ax.set_facecolor(item['color'])
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(f"{item['id']}\n{ID_TO_CLASS[item['id']]}", fontsize=7, labelpad=4)
        for spine in ax.spines.values():
            spine.set(edgecolor="black", linewidth=0.5)

    plt.suptitle("Paleta de cores das classes", fontsize=11, fontweight="bold")
    plt.tight_layout()
    plt.show()


# def read_parameters_inputted_by_user() -> dict:
#     with open(_CONFIG_PATH, "r") as f:
#         config = yaml.safe_load(f)
#     return config


class exploratory_data_analysis:

    @staticmethod
    def get_stats_from_splits(train_dataset, val_dataset, test_dataset):
        CACHE_DIR = Path("../data/cache")
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

        cache_train = CACHE_DIR / "metricas_train.pkl"
        cache_val   = CACHE_DIR / "metricas_val.pkl"
        cache_test  = CACHE_DIR / "metricas_test.pkl"

        if cache_train.exists() and cache_val.exists() and cache_test.exists():
            metricas_train = exploratory_data_analysis.carregar_metricas(cache_train)
            metricas_val   = exploratory_data_analysis.carregar_metricas(cache_val)
            metricas_test  = exploratory_data_analysis.carregar_metricas(cache_test)
        else:
            metricas_train = exploratory_data_analysis.extrair_metricas(train_dataset)
            metricas_val   = exploratory_data_analysis.extrair_metricas(val_dataset)
            metricas_test  = exploratory_data_analysis.extrair_metricas(test_dataset)

            exploratory_data_analysis.salvar_metricas(metricas_train, cache_train)
            exploratory_data_analysis.salvar_metricas(metricas_val,   cache_val)
            exploratory_data_analysis.salvar_metricas(metricas_test,  cache_test)
        
        return metricas_train, metricas_val, metricas_test

    @staticmethod
    def _calcular_ndvi(rgb_path, nir_path):
        rgb = mpimg.imread(rgb_path)
        nir = mpimg.imread(nir_path).astype(float)
        red = rgb[:, :, 0].astype(float)
        denominador = nir + red
        numerador   = nir - red
        return np.divide(numerador, denominador, out=np.zeros_like(denominador), where=(denominador != 0))

    @staticmethod
    def _fusao_labels(name_arquivo, labels_dirs):
        mascara_final       = None
        classes_encontradas = []

        for label_dir in labels_dirs:
            mascara_atual = mpimg.imread(label_dir / name_arquivo)
            if np.any(mascara_atual > 0):
                classes_encontradas.append(label_dir.name)
            mascara_final = mascara_atual if mascara_final is None else np.maximum(mascara_final, mascara_atual)

        if not classes_encontradas:
            classes_encontradas = ["Background"]

        return mascara_final, classes_encontradas

    @staticmethod
    def _extrair_dados_imagem(filename: str, labels_dirs: list) -> dict:
        instancias_imagem = {}
        filename_png = f"{filename.split('.')[0]}.png"

        for label_dir in labels_dirs:
            img_path = label_dir / filename_png
            if img_path.exists():
                mask = np.array(Image.open(img_path))
                qtd_pixels = np.sum(mask > 0)
                if qtd_pixels > 0:
                    instancias_imagem[label_dir.name] = qtd_pixels

        return instancias_imagem

    @staticmethod
    def extrair_metricas(split_dataset) -> dict:
        labels_dirs   = split_dataset.labels_dirs
        paths         = split_dataset.paths
        nomes_classes = [d.name for d in labels_dirs]
        arquivos      = split_dataset.lista_ids

        print(f"Executando varredura em {len(arquivos)} imagens ({split_dataset.caminho_split.name})...")

        dados_instancias   = {}
        matriz_coocorrencia = np.zeros((len(nomes_classes), len(nomes_classes)), dtype=int)
        class_to_idx       = {nome: idx for idx, nome in enumerate(nomes_classes)}

        with ThreadPoolExecutor() as executor:
            resultados = list(tqdm(
                executor.map(
                    lambda f: exploratory_data_analysis._extrair_dados_imagem(f, labels_dirs),
                    arquivos,
                ),
                total=len(arquivos),
            ))

        for instancias_imagem in resultados:
            classes_presentes = list(instancias_imagem.keys())

            for classe, pixels in instancias_imagem.items():
                dados_instancias.setdefault(classe, []).append(pixels)

            for classe_a in classes_presentes:
                for classe_b in classes_presentes:
                    matriz_coocorrencia[class_to_idx[classe_a], class_to_idx[classe_b]] += 1

        contagem_imagens = {c: len(v) for c, v in dados_instancias.items()}
        contagem_pixels  = {c: sum(v) for c, v in dados_instancias.items()}
        df_escala        = pd.DataFrame([
            {"Classe": classe, "Pixels": area}
            for classe, tamanhos in dados_instancias.items()
            for area in tamanhos
        ])

        return {
            "contagem_imagens":    contagem_imagens,
            "contagem_pixels":     contagem_pixels,
            "matriz_coocorrencia": matriz_coocorrencia,
            "df_escala":           df_escala,
            "nomes_classes":       nomes_classes,
            "total_imagens":       len(arquivos),
        }

    @staticmethod
    def plot_consistencia_split(metricas_val: dict, metricas_test: dict) -> None:
        contagem_val  = metricas_val["contagem_imagens"]
        contagem_test = metricas_test["contagem_imagens"]
        total_val     = metricas_val["total_imagens"]
        total_test    = metricas_test["total_imagens"]
        total_original = total_val + total_test

        todas_classes = sorted(contagem_val.keys() | contagem_test.keys())

        # Reconstrói o Val Original somando val + test
        contagem_original = {
            cls: contagem_val.get(cls, 0) + contagem_test.get(cls, 0)
            for cls in todas_classes
        }

        splits_plot = [
            ("Val Original",   contagem_original, total_original),
            ("Val (adaptado)", contagem_val,       total_val),
        ]

        pcts_por_split = [
            [contagem.get(cls, 0) / total * 100 for cls in todas_classes]
            for _, contagem, total in splits_plot
        ]
        x_max = max(pct for pcts in pcts_por_split for pct in pcts) * 1.15

        fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=True)
        fig.suptitle(
            "Consistência do Split — Val Original vs Val (adaptado)",
            fontsize=15, fontweight="bold", y=1.02,
        )

        for ax, (nome_split, contagem, total), pcts in zip(axes, splits_plot, pcts_por_split):
            sns.barplot(
                x=pcts, y=todas_classes, hue=todas_classes,
                palette="viridis", legend=False, ax=ax,
            )
            ax.set_xlim(0, x_max)
            ax.set_title(f"{nome_split}\n({total} imagens)", fontsize=12, fontweight="bold")
            ax.set_xlabel("% de imagens onde a classe aparece", fontsize=10)
            ax.set_ylabel("Classes" if ax is axes[0] else "", fontsize=10)

            for i, (cls, pct) in enumerate(zip(todas_classes, pcts)):
                v = contagem.get(cls, 0)
                ax.text(pct + (x_max * 0.01), i, f"{v} ({pct:.1f}%)", va="center", fontsize=9)

            sns.despine(ax=ax)

        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_frequencia_classes(splits: list[tuple[str, dict, int]]) -> None:
        todas_classes = sorted({cls for _, contagem, _ in splits for cls in contagem})

        # Calcula porcentagens e define escala x uniforme com o maior valor entre os 3 splits
        pcts_por_split = [
            [contagem.get(cls, 0) / total * 100 for cls in todas_classes]
            for _, contagem, total in splits
        ]
        x_max = max(pct for pcts in pcts_por_split for pct in pcts) * 1.15

        fig, axes = plt.subplots(1, len(splits), figsize=(22, 7), sharey=True)
        fig.suptitle(
            "Frequência das Classes por Imagem - Agriculture Vision",
            fontsize=15, fontweight="bold", y=1.02,
        )

        for ax, (nome_split, contagem, total), pcts in zip(axes, splits, pcts_por_split):
            sns.barplot(
                x=pcts, y=todas_classes, hue=todas_classes,
                palette="viridis", legend=False, ax=ax,
            )
            ax.set_xlim(0, x_max)
            ax.set_title(f"{nome_split}\n({total} imagens)", fontsize=12, fontweight="bold")
            ax.set_xlabel("% de imagens onde a classe aparece", fontsize=10)
            ax.set_ylabel("Classes" if ax is axes[0] else "", fontsize=10)

            for i, (cls, pct) in enumerate(zip(todas_classes, pcts)):
                v = contagem.get(cls, 0)
                ax.text(pct + (x_max * 0.01), i, f"{v} ({pct:.1f}%)", va="center", fontsize=9)

            sns.despine(ax=ax)

        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_area_pixels_log(splits: list[tuple[str, dict]]) -> None:
        todas_classes = sorted({cls for _, contagem in splits for cls in contagem})

        fig, axes = plt.subplots(1, len(splits), figsize=(22, 7), sharey=True, sharex=True)
        fig.suptitle(
            "Área Total Ocupada por Classe - Agriculture Vision\n(Total de Pixels em Escala Logarítmica)",
            fontsize=15, fontweight="bold", y=1.02,
        )

        for ax, (nome_split, contagem) in zip(axes, splits):
            valores = [contagem.get(cls, 0) for cls in todas_classes]

            sns.barplot(
                x=valores, y=todas_classes, hue=todas_classes,
                palette="magma", legend=False, ax=ax,
            )
            ax.set_xscale("log")
            ax.set_title(nome_split, fontsize=12, fontweight="bold")
            ax.set_xlabel("Número de Pixels (Log)", fontsize=10)
            ax.set_ylabel("Classes" if ax is axes[0] else "", fontsize=10)

            for i, v in enumerate(valores):
                if v > 0:
                    ax.text(v * 1.15, i, f"{v:,}", va="center", fontsize=9)

            sns.despine(ax=ax)

        plt.tight_layout()
        plt.show()

    @staticmethod
    def plot_distribuicao_escala(splits: list[tuple[str, pd.DataFrame]]) -> None:
        todas_classes     = sorted({cls for _, df in splits for cls in df["Classe"].unique()})
        area_total_imagem = 512 * 512
        palette           = dict(zip(todas_classes, sns.color_palette("vlag", len(todas_classes))))

        fig, axes = plt.subplots(1, len(splits), figsize=(22, 8), sharey=True, sharex=True)
        fig.suptitle(
            "Distribuição de Escala das Instâncias - Agriculture Vision\n(Tamanho físico em pixels mapeado em Escala Logarítmica)",
            fontsize=15, fontweight="bold", y=1.02,
        )

        for ax, (nome_split, df_escala) in zip(axes, splits):
            sns.boxplot(
                x="Pixels", y="Classe", data=df_escala,
                order=todas_classes, ax=ax,
                hue="Classe", palette=palette,
                width=0.6, showfliers=False, legend=False,
            )
            sns.stripplot(
                x="Pixels", y="Classe", data=df_escala,
                order=todas_classes, ax=ax,
                color=".3", alpha=0.05, size=2,
            )

            ax.set_xscale("log")
            ax.set_title(nome_split, fontsize=12, fontweight="bold")
            ax.set_xlabel("Tamanho da Instância em Pixels (Log)", fontsize=10)
            ax.set_ylabel("Classes" if ax is axes[0] else "", fontsize=10)
            ax.grid(axis="x", linestyle="--", alpha=0.7)
            ax.axvline(
                area_total_imagem, color="red", linestyle=":",
                label=f"Área Total da Imagem ({area_total_imagem:,} px)",
            )
            ax.legend(loc="lower right", fontsize=8)

            sns.despine(ax=ax)

        plt.tight_layout()
        plt.show()

    @staticmethod
    def salvar_metricas(metricas: dict, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(metricas, f)
        print(f"Métricas salvas em {path}")

    @staticmethod
    def carregar_metricas(path: str | Path) -> dict:
        with open(Path(path), "rb") as f:
            return pickle.load(f)

    @staticmethod
    def show_samples(mode: str, split_dataset, num_amostras: int = 3):
        paths       = split_dataset.paths
        labels_dirs = split_dataset.labels_dirs
        is_test     = mode.upper() == "TEST"
        num_cols    = 5 if is_test else 6

        arquivos_rgb = [f.name for f in paths["rgb"].iterdir() if f.is_file()]
        amostras     = random.sample(arquivos_rgb, num_amostras)

        for img_name in amostras:
            sample_id = img_name.split(".")[0]

            rgb_path      = paths["rgb"]        / img_name
            nir_path      = paths["nir"]        / img_name
            mask_path     = paths["masks"]      / f"{sample_id}.png"
            boundary_path = paths["boundaries"] / f"{sample_id}.png"

            img_rgb      = np.array(Image.open(rgb_path))
            img_nir      = np.array(Image.open(nir_path))
            img_mask     = np.array(Image.open(mask_path))
            img_boundary = np.array(Image.open(boundary_path))
            ndvi_array   = exploratory_data_analysis._calcular_ndvi(rgb_path, nir_path)

            fig, axes = plt.subplots(2, num_cols, figsize=(20, 9))
            fig.suptitle(f"Sample ID: {sample_id} ({mode.upper()})", fontsize=16, fontweight="bold")

            for ax in axes.flat:
                ax.set(xticks=[], yticks=[])
                for spine in ax.spines.values():
                    spine.set(edgecolor="black", linewidth=0.8)

            axes[1, 2].axis("off")
            axes[1, 3].axis("off")
            if not is_test:
                axes[1, 4].axis("off")

            axes[0, 0].imshow(img_rgb, vmin=0, vmax=255)
            axes[0, 0].set_title("RGB (Raw)")
            axes[0, 1].imshow(img_nir, cmap="gray", vmin=0, vmax=255)
            axes[0, 1].set_title("NIR (Raw)")
            axes[0, 2].imshow(img_mask, cmap="gray", vmin=0, vmax=255)
            axes[0, 2].set_title("Mask")
            axes[0, 3].imshow(img_boundary, cmap="gray", vmin=0, vmax=255)
            axes[0, 3].set_title("Boundary")

            col_ndvi = 4 if is_test else 5

            if not is_test:
                img_labels, lista_classes = exploratory_data_analysis._fusao_labels(f"{sample_id}.png", labels_dirs)
                axes[0, 4].imshow(img_labels, cmap="gray", vmin=0, vmax=1)
                axes[0, 4].set_title(", ".join(lista_classes), fontsize=10)

            img_ndvi = axes[0, col_ndvi].imshow(ndvi_array, cmap="RdYlGn", vmin=-1, vmax=1)
            axes[0, col_ndvi].set_title("NDVI (Raw)")
            fig.colorbar(img_ndvi, cax=axes[0, col_ndvi].inset_axes([1.05, 0.0, 0.05, 1.0]))

            if is_test:
                roi = (img_mask > 0) & (img_boundary > 0)
            else:
                roi = (img_labels > 0) & (img_mask > 0) & (img_boundary > 0)

            rgb_recortado  = np.where(np.expand_dims(roi, axis=-1), img_rgb, 0).astype(img_rgb.dtype)
            nir_recortado  = np.where(roi, img_nir, 0).astype(img_nir.dtype)
            ndvi_recortado = np.where(roi, ndvi_array, np.nan)

            axes[1, 0].imshow(rgb_recortado, vmin=0, vmax=255)
            axes[1, 0].set_title("RGB (Region of Interest)")
            axes[1, 1].imshow(nir_recortado, cmap="gray", vmin=0, vmax=255)
            axes[1, 1].set_title("NIR (Region of Interest)")

            img_ndvi_r = axes[1, col_ndvi].imshow(ndvi_recortado, cmap="RdYlGn", vmin=-1, vmax=1)
            axes[1, col_ndvi].set_title("NDVI (Region of Interest)")
            fig.colorbar(img_ndvi_r, cax=axes[1, col_ndvi].inset_axes([1.05, 0.0, 0.05, 1.0]))

            plt.tight_layout()
            plt.show()
