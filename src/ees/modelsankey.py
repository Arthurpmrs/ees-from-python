import os
import sys
import math

from numpy import i0
sys.path.append(os.path.join(os.getcwd(), 'src'))
from utilities import get_base_folder
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey
import plotly.graph_objects as go
import random


class ModelSankey:

    def __init__(self, EES_model: str, run_id: str, display_title: str):
        self.base_path = get_base_folder(EES_model)
        self.run_id = run_id
        self.paths = self.set_paths()
        self.display_title = display_title

    def set_paths(self):
        paths = {
            'data': os.path.join(self.base_path, '.solver', self.run_id)
        }

        for path in paths.values():
            if not os.path.exists(path):
                os.makedirs(path)

        return paths

    def load_exergy_data(self):
        filename_arrays = os.path.join(self.paths.get("data"), "clean_arrays.csv")
        df_arrays = pd.read_csv(filename_arrays, delimiter=";", decimal=",")
        exergy = df_arrays["ex"]
        exergy.index = list(range(1, 39))

        filename_outputs = os.path.join(self.paths.get("data"), "outputs.xlsx")
        outputs = pd.read_excel(filename_outputs)
        outputs = outputs.set_index("Unnamed: 0")

        labels = ["Combustível", "Brayton", "SRA", "HDH", "Produtos", "Perdas", "Exaustão Brayton",
                  "Exaustão SRA", "Exaustão HDH"]

        data = [
            ["Combustível", "Brayton", exergy[9]],
            ["Brayton", "Produtos", outputs.loc["W_net", 0]],
            ["Brayton", "Perdas", outputs.loc["Exd_brayton", 0]],
            ["Brayton", "Exaustão Brayton", exergy[6]],
            ["Exaustão Brayton", "SRA", exergy[6]],
            ["SRA", "Exaustão SRA", exergy[7]],
            ["SRA", "Produtos", exergy[31] - exergy[30]],
            ["SRA", "Perdas", outputs.loc["Exd_sra", 0]],
            ["Exaustão SRA", "HDH", exergy[7]],
            ["HDH", "Exaustão HDH", exergy[8]],
            ["HDH", "Produtos", exergy[38]],
            ["HDH", "Perdas", outputs.loc["Exd_hdh", 0]]
        ]
        for i, label in enumerate(labels):
            for j, t in enumerate(data):
                for k, item in enumerate(t):
                    if item == label:
                        data[j][k] = i
        return data

    def get_titles(self):
        pass

    def generate(self):
        data = self.load_exergy_data()

        source = [item[0] for item in data]
        target = [item[1] for item in data]
        value = [item[2] for item in data]
        labels = ["Combustível", "Brayton", "SRA", "HDH", "Produtos", "Perdas", "Exaustão Brayton",
                  "Exaustão SRA", "Exaustão"]

        node_colors = ["rgba(255, 215, 0, 1)", "rgba(255,0,255, 1)", "rgba(0,255,0, 1)", "rgba(0, 0, 255, 1)",
                       "rgba(255, 215, 0, 1)", "rgba(255,0,0, 1)", "rgba(255,0,255, 1)", "rgba(0,255,0, 1)", "rgba(0, 0, 255, 1)"]
        link_colors = [color.replace("1)", "0.4)") for color in node_colors]

        fig = go.Figure(data=[go.Sankey(
            valueformat=".2f",
            valuesuffix=" kW",
            arrangement="snap",
            node=dict(
                pad=15,
                thickness=10,
                line=dict(color="black", width=0.5),
                label=labels,
                color=node_colors,
                x=[0.05, 0.25, 0.58, 0.82, 1, 1, 0.42, 0.68, 1],
                y=[0.5, 0.5, 0.7, 0.7, 1, 0.3, 0.6, 0.7, 0.1],
            ),
            link=dict(
                source=source,  # indices correspond to labels, eg A1, A2, A1, B1, ...
                target=target,
                value=value,
                color=[link_colors[i] for i in source],
                label=[f"{v:.2f} kW" for v in value]
            ))])

        fig.update_layout(title_text=self.display_title, font_size=14, width=1000, height=500, showlegend=True)
        final_path = os.path.join(self.paths["data"], "sankey_diagram.pdf")
        fig.write_image(final_path)
        fig.show()


def main():
    EES_model = r'C:\Users\55199\Meu Drive\[Unicamp]\[Dissertação]\01 - Algoritmo\Analise\trigeracao_LiBrH2O.EES'
    run_id = "CASO BASE"

    sankey = ModelSankey(EES_model, run_id, "Caso Base")
    sankey.load_exergy_data()
    sankey.generate()


if __name__ == "__main__":
    main()
