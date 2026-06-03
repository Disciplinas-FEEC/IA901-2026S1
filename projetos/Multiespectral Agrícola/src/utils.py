import pickle
import random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
from PIL import Image
from tqdm import tqdm
import yaml

_CONFIG_PATH = "../../config.yaml"


def read_parameters_inputted_by_user() -> dict:
    with open(_CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
    return config


class exploratory_data_analysis:

    @staticmethod
    def get_stats_from_splits(train_dataset, val_dataset, test_dataset):
        CACHE_DIR = Path("../../data/cache")
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
    def show_samples(split_dataset, num_amostras: int = 3):
        paths       = split_dataset.paths
        labels_dirs = split_dataset.labels_dirs
        mode        = split_dataset.caminho_split.name
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
