import os
import sys
import numpy as np
from numpy.core.defchararray import index
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from .utilities import check_model_path, get_base_folder, add_folder, ParamAnalysisMissingError


class OptParamGraphs:

    def __init__(self, EES_model: str, run_ID: str, results: dict):
        self.base_path = get_base_folder(EES_model)
        self.run_ID = run_ID
        self.results = results
        self.plots_folder = self.set_plots_folder()
        self.set_matplotlib_globalconfig()

    def set_plots_folder(self) -> str:
        plots_folder = add_folder(self.base_path, ".optParamAnalysis", self.run_ID, ".plots")
        return plots_folder

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

        # matplotlib.rcParams["axes.prop_cycle"] = matplotlib.cycler(
        #     color=["r", "b", "g", "m", "k"]
        # )
        matplotlib.rcParams["ytick.labelsize"] = 15
        matplotlib.rcParams["xtick.labelsize"] = 15

    def get_titles(self, lang: str) -> dict:
        if lang in ["pt-BR", "pt_BR", "ptbr"]:
            titles = {

            }
        elif lang in ["en-US", "en_US", "enus"]:
            titles = {

            }
        else:
            raise ValueError("Linguagem não suportada!")

        return titles

    def generate(self):

        for param, values in self.results.items():
            labels = []
            generations = []
            times = []
            target_values = []
            decision_variables = []
            for idx, value in values.items():
                print(value["param_value"])

            old_dict = values[list(values.keys())[-1]]["param_value"][next(iter(values[list(values.keys())[-1]]["param_value"]))]
            for idx, value in values.items():
                print(value["param_value"])
                print(value["param_studied"])
                target_variable = list(value["best_target"].keys())[0]
                for p, v in value["param_value"].items():
                    if isinstance(v, dict):
                        v_unclean = v
                        v = OptParamGraphs.difference(v_unclean, old_dict)
                        old_dict = v_unclean
                labels.append(str(v))
                generations.append(value["generations"])
                times.append(value["evolution_time"])
                target_values.append(value["best_target"][next(iter(value["best_target"]))])
                decision_variables.append(value["best_individual"])

            print(decision_variables)
            dv_df = pd.DataFrame(decision_variables, index=labels)
            dv = dv_df.to_dict(orient='list')
            print(dv_df)
            width = 0.35
            fig = plt.figure(figsize=(14, 8))
            # plt.title(f"Análise de {param}")
            # plt.xlabel(param)
            sub1 = fig.add_subplot(2, 2, 1)
            sub1.bar(labels, target_values, width=width)
            sub1.set_title(target_variable)
            sub1.set_ylabel(target_variable)

            sub0 = fig.add_subplot(2, 2, 2)
            dv_df.plot(kind='bar', stacked=False, ax=sub0)

            sub2 = fig.add_subplot(2, 2, 3)
            sub2.bar(labels, generations, width=width)
            sub2.set_title("Gerações")
            sub2.set_ylabel("Gerações")
            print(generations)

            sub3 = fig.add_subplot(2, 2, 4)
            sub3.bar(labels, times, width=width)
            sub3.set_title("Tempo de Convergência")
            sub3.set_ylabel("Tempo (s)")
            print(times)
            plt.tight_layout()

            filename = os.path.join(self.plots_folder, f"analysis-of-{param}.svg")
            plt.savefig(filename)
            fig.clf()

    @staticmethod
    def difference(d1, d2):
        for (k1, v1), (k2, v2) in zip(d1.items(), d2.items()):
            if v1 != v2:
                return v2
