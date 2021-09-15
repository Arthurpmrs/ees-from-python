from graphs_default import GraphsDefault
from graphs_sys_eff_decomp import GraphsSysEffDecomp
from graphs_exd_hdh import GraphsHDHExd
from graphs_exd_sys import GraphsSysExd
from graphs_effectiveness_hdh import GraphsEffectivenessHDH


def main():
    base_paths = [r"models\trigeracao_LiBrH2O", r"models\trigeracao_NH3H2O"]

    graph = GraphsDefault(base_paths, 'T[22]')
    graph.generate(r'$ T_{22} $ ($^{\circ}$C)', lang='en-US')
    graph.generate(r'$ T_{22} $ ($^{\circ}$C)', lang='pt-BR')
    del graph

    graph = GraphsDefault(base_paths, "T[19]")
    graph.generate(r"$ T_{19} $ ($^{\circ}$C)", lang="en-US")
    graph.generate(r"$ T_{19} $ ($^{\circ}$C)", lang="pt-BR")
    del graph

    graph = GraphsDefault(base_paths, 'T[10]')
    graph.generate(r'$ T_{10} $ ($^{\circ}$C)', lang='en-US')
    graph.generate(r'$ T_{10} $ ($^{\circ}$C)', lang='pt-BR')
    del graph

    graph = GraphsDefault(base_paths, 'T[13]')
    graph.generate(r'$ T_{13} $ ($^{\circ}$C)', lang='en-US')
    graph.generate(r'$ T_{13} $ ($^{\circ}$C)', lang='pt-BR')
    del graph

    graph = GraphsDefault(base_paths, 'epsilon_hx')
    graph.generate(r'$ \varepsilon_{SHX} $', lang='en-US')
    graph.generate(r'$ \varepsilon_{SHX} $', lang='pt-BR')
    del graph

    # m_dot[9]
    graph = GraphsDefault(base_paths, 'm_dot[9]')
    graph.generate(r'$ \dot{m}_{9} $ (kg/s)', lang='en-US')
    graph.generate(r'$ \dot{m}_{9} $ (kg/s)', lang='pt-BR')

    decompgraph = GraphsSysEffDecomp(base_paths, 'm_dot[9]')
    decompgraph.generate(r'$ \dot{m}_{9} $ (kg/s)', lang='en-US')
    decompgraph.generate(r'$ \dot{m}_{9} $ (kg/s)', lang='pt-BR')
    del graph, decompgraph

    # MR
    graph = GraphsDefault(base_paths, "MR")
    graph.generate("MR", lang="en-US")
    graph.generate("MR", lang="pt-BR")

    exdgraph = GraphsHDHExd(base_paths, "MR")
    exdgraph.generate('MR', lang="pt-BR")
    exdgraph.generate('MR', lang="en-US")
    del graph, exdgraph

    # Salinidade
    graph = GraphsDefault(base_paths, 'salinity')
    graph.generate('Salinity (g/kg)', lang='en-US')
    graph.generate('Salinidade (g/kg)', lang='pt-BR')
    del graph

    # T[34]
    graph = GraphsDefault(base_paths, 'T[34]')
    for _, df in graph.dfs.items():
        df.drop(index=6, inplace=True)
    graph.generate(r'$ T_{34} $ ($^{\circ}$C)', lang='en-US')
    graph.generate(r'$ T_{34} $ ($^{\circ}$C)', lang='pt-BR')
    del graph

    # X_CH4
    graph = GraphsDefault(base_paths, 'X_biogas_ch4')
    graph.generate(r'$ X_{CH_4} $', lang='en-US')
    graph.generate(r'$ X_{CH_4} $', lang='pt-BR')

    exdgraph = GraphsSysExd(base_paths, 'X_biogas_ch4')
    exdgraph.generate(r'$ X_{CH_4} $', lang='en-US')
    exdgraph.generate(r'$ X_{CH_4} $', lang='pt-BR')
    del graph, exdgraph

    graph = GraphsEffectivenessHDH(base_paths, lang='pt-BR')
    graph.generate()
    del graph
    graph = GraphsEffectivenessHDH(base_paths, lang='en-US')
    graph.generate()
    graphsexd = GraphsHDHExd(base_paths, 'epsilon_d')
    graphsexd.generate(r'$ \varepsilon_{D} $', lang='pt-BR')
    graphsexd.generate(r'$ \varepsilon_{D} $', lang='en-US')


def main2():
    # base_paths = [
    #     r"C:\Root\Universidade\Mestrado\Dissertação\Analises\models\trigeracao_LiBrH2O",
    #     r"C:\Root\Universidade\Mestrado\Dissertação\Analises\models\trigeracao_NH3H2O",
    # ]
    base_paths = [r"C:\Root\Universidade\Mestrado\Analise\trigeracao_LiBrH2O2"]

    graph = GraphsDefault(base_paths, 'T[32]')
    # graph.dfs["trigeracao_LiBrH2O"].drop(index=14, inplace=True)
    graph.generate(r'$ T_{32} $ ($^{\circ}$C)', lang='en-US')
    graph.generate(r'$ T_{32} $ ($^{\circ}$C)', lang='pt-BR')
    del graph


if __name__ == "__main__":
    main2()
