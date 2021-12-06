import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'src'))
from ees.parametric_graphs import Graphs
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager


class DollarAnalisys():

    def __init__(self, EES_model):
        self.paths = self.set_paths(EES_model)
        self.df = self.get_df()
        self.set_matplotlib_globalconfig()

    def set_paths(self, EES_model):
        model_folder = os.path.dirname(EES_model)
        model_filename = '.'.join(os.path.basename(EES_model).split(".")[:-1])
        base_path = os.path.join(
            model_folder, model_filename, ".parametric"
        )
        paths = {
            "base_path": base_path,
            "csv": os.path.join(base_path, ".results", "dolar", "parametric_result.csv"),
            "plot": os.path.join(base_path, ".plots", "analiseDolar")
        }
        if not os.path.exists(paths.get("plot")):
            os.makedirs(paths.get("plot"))
        return paths

    def get_df(self):
        filepath = self.paths.get("csv")
        return pd.read_csv(filepath, sep=";")

    def set_matplotlib_globalconfig(self):
        plt.style.use("ggplot")

        font_dir = [r"C:\Root\Download\computer-modern"]
        for font in font_manager.findSystemFonts(font_dir):
            font_manager.fontManager.addfont(font)

        matplotlib.rcParams["mathtext.fontset"] = "cm"
        matplotlib.rcParams["font.family"] = "CMU Serif"

        axes = {
            "labelsize": 22,
            "titlesize": 18,
            "titleweight": "bold",
            "labelweight": "bold",
        }
        matplotlib.rc("axes", **axes)

        lines = {"linewidth": 2}
        matplotlib.rc("lines", **lines)

        legends = {"fontsize": 14}
        matplotlib.rc("legend", **legends)

        savefig = {"dpi": 300}
        matplotlib.rc("savefig", **savefig)

        matplotlib.rcParams["axes.prop_cycle"] = matplotlib.cycler(
            color=["r", "b", "g", "m", "k"]
        )
        matplotlib.rcParams["ytick.labelsize"] = 15
        matplotlib.rcParams["xtick.labelsize"] = 15

    def get_titles(self, lang):
        if lang in ["pt-BR", "pt_BR", "ptbr"]:
            titles = {
                "num": "Tempo de Payback Simples vs Preço do Dólar",
                "title": "Tempo de Payback Simples vs Preço do Dólar",
                "dolar": "Preço do Dolar (R$)",
                "tpb": "Tempo de Payback Simples (anos)"
            }
        elif lang in ["en-US", "en_US", "enus"]:
            titles = {
                "num": "Payback Time vs Dollar prices",
                "title": "Payback Time vs Dollar prices",
                "dolar": "Dollar Price (R$)",
                "tpb": "Payback Time (years)"
            }
        else:
            raise ValueError("Linguagem não suportada!")

        return titles

    def generate(self, lang):
        titles = self.get_titles(lang)

        # Dessalinização
        fig1, ax1 = plt.subplots(1, 1, figsize=(8, 7), num=titles["num"])
        ax1.set_title(titles["title"])
        ax1.set_xlabel(titles["dolar"])
        ax1.set_ylabel(titles["tpb"])

        ax1.plot(self.df["dolar"], self.df["payback_simples_2"])

        # Axis Limits
        ax1.set_ylim(
            0.95 * self.df["payback_simples_2"].min(),
            1.05 * self.df["payback_simples_2"].max(),
        )

        fig1.tight_layout()
        fig1.savefig(
            os.path.join(self.paths.get("plot"),
                         f"plot_{lang}_dolar_vs_payback.svg")
        )
