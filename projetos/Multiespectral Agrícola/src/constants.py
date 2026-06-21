import matplotlib
import yaml
from pathlib import Path

_colors = list(matplotlib.colormaps['tab10'].colors)  # 10 cores RGB floats

CLASSES_DICT = {
    'background':          {'id': 0, 'color': (0.0, 0.0, 0.0)},
    'double_plant':        {'id': 1, 'color': _colors[0]},
    'drydown':             {'id': 2, 'color': _colors[1]},
    'endrow':              {'id': 3, 'color': _colors[2]},
    'nutrient_deficiency': {'id': 4, 'color': _colors[3]},
    'planter_skip':        {'id': 5, 'color': _colors[4]},
    'water':               {'id': 6, 'color': _colors[5]},
    'waterway':            {'id': 7, 'color': _colors[6]},
    'weed_cluster':        {'id': 8, 'color': _colors[8]},  # pula índice 7 (cinza)
    'storm_damage':        {'id': 9, 'color': _colors[9]},
}

BAND_DICT = {
    'r': {'id': 0,
          'name': 'Red', 'cmap': 'Reds',
          'vmin': 0, 'vmax': 1,
          'colorbar': False},
    'g': {'id': 1,
          'name': 'Green', 'cmap': 'Greens',
          'vmin': 0, 'vmax': 1,
          'colorbar': False},
    'b': {'id': 2,
          'name': 'Blue', 'cmap': 'Blues',
          'vmin': 0, 'vmax': 1,
          'colorbar': False},
    'n': {'id': 0,
          'name': 'NIR', 'cmap': 'gray',
          'vmin': 0, 'vmax': 1,
          'colorbar': False},
    'v': {'id': 0,
          'name': 'NDVI', 'cmap': 'RdYlGn',
          'vmin': -1, 'vmax': 1,
          'colorbar': True},
    'w': {'id': 0,
          'name': 'NDWI', 'cmap': 'RdYlBu',
          'vmin': -1, 'vmax': 1,
          'colorbar': True},
}

# CLASS_MAP    = {name: info['id']          for name, info in CLASSES_DICT.items()}
# CLASS_COLORS = {info['id']: info['color'] for info in CLASSES_DICT.values()}

# para normalizar os canais RGB de entrada, utilizaram-se
# estatísticas do modelo que foi pré-treinado no ImageNet, a ResNet
# Canais sem estatística (NIR/NDVI/NDWI) ficam sem normalização (mean=0, std=1).
# https://www.geeksforgeeks.org/python/how-to-normalize-images-in-pytorch/
IMAGENET_MEAN = {'r': 0.485, 'g': 0.456, 'b': 0.406}
IMAGENET_STD  = {'r': 0.229, 'g': 0.224, 'b': 0.225}

_PROJECT_ROOT = Path(__file__).parent.parent
_CONFIG_PATH = _PROJECT_ROOT / "config.yaml"
with open(_CONFIG_PATH, "r") as _f:
    _config = yaml.safe_load(_f)

DATASET_DIR              = _config['dataset_path']
INPUT_CHANNELS           = _config['input_channels']
CLASSES2EVAL             = _config['classes_to_evaluate']
BATCH_SIZE               = _config['model_hyperparameters']['batch_size']
IS_WEIGHTED_LOSS         = _config['model_hyperparameters']['is_weighted_loss']
IS_SPLIT_VALIDATION_SET  = _config['code_variables']['isSplitValidationSet']
TAX_FOR_VALIDATION_SET   = _config['code_variables']['taxForValidationSet']
SEED                     = _config['code_variables']['seed']



CHECKPOINT_DIR = _PROJECT_ROOT / f"experiments/checkpoints/{INPUT_CHANNELS}_v3"
TENSORBOARD_DIR = _PROJECT_ROOT / f"experiments/tensorboard/{INPUT_CHANNELS}_v3"
CACHE_DIR = _PROJECT_ROOT / "data/cache"