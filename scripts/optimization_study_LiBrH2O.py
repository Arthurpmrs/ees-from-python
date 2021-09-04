import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'src'))
import json
from icecream import ic
from ees.optimization import OptimizationStudy
from ees.optimization_ga import GAOptimizationStudy
from ees.optimization_graphs import OptGraph


def main(EES_exe, EES_model, inputs, outputs, decision_variables, base_config):
    """Run one optimization case."""
    eesopt = GAOptimizationStudy(EES_exe, EES_model, inputs, outputs)
    eesopt.set_decision_variables(decision_variables)
    eesopt.set_target_variable("EUF_sys", r"$ EUF_{sys} $")
    # eesopt.set_target_variable("psi_sys_1", r"$ \psi_{sys} $")
    # eesopt.set_target_variable("m_dot[38]", r"$ \dot{m}_{38} $")
    eesopt.execute_GA(base_config)
    graph = OptGraph(r"C:\Root\Universidade\Mestrado\Dissertação\Analises\models\trigeracao_LiBrH2O")
    graph.generate(r"$ EUF_{sys} $", lang="pt-BR")
    graph.generate(r"$ EUF_{sys} $", lang="en-US")


def param_analysis(EES_exe, EES_model, inputs, outputs, decision_variables, base_config):
    model_filename = os.path.basename(EES_model).split(".")[0]
    model_folder = os.path.join(os.path.dirname(EES_model), model_filename)
    opt_analysis_folder = os.path.join(model_folder, ".optAnalysis")

    if not os.path.exists(opt_analysis_folder):
        os.makedirs(opt_analysis_folder)

    low = tuple([v[0] for _, v in decision_variables.items()])
    up = tuple([v[1] for _, v in decision_variables.items()])

    params = {
        "population": [10, 15, 25, 50, 100, 200],
        "crossover_rates": [
            {'rate': 0.2, 'method': 'cxTwoPoint', 'params': {}},
            {'rate': 0.3, 'method': 'cxTwoPoint', 'params': {}},
            {'rate': 0.4, 'method': 'cxTwoPoint', 'params': {}},
            {'rate': 0.5, 'method': 'cxTwoPoint', 'params': {}},
            {'rate': 0.6, 'method': 'cxTwoPoint', 'params': {}},
            {'rate': 0.7, 'method': 'cxTwoPoint', 'params': {}},
            {'rate': 0.8, 'method': 'cxTwoPoint', 'params': {}}
        ],
        "crossover_methods": [
            {'rate': 0.5, 'method': 'cxTwoPoint', 'params': {}},
            {'rate': 0.5, 'method': 'cxUniform', 'params': {'indpb': 0.05}},
            {'rate': 0.5, 'method': 'cxBlend', 'params': {'alpha': 0.45}}
        ],
        "mutation_rates": [
            {'rate': 0.01, 'method': 'mutFlipBit', 'params': {'indpb': 0.05}},
            {'rate': 0.05, 'method': 'mutFlipBit', 'params': {'indpb': 0.05}},
            {'rate': 0.10, 'method': 'mutFlipBit', 'params': {'indpb': 0.05}},
            {'rate': 0.15, 'method': 'mutFlipBit', 'params': {'indpb': 0.05}},
            {'rate': 0.20, 'method': 'mutFlipBit', 'params': {'indpb': 0.05}},
            {'rate': 0.25, 'method': 'mutFlipBit', 'params': {'indpb': 0.05}}
        ],
        "mutation_methods": [
            {'rate': 0.15, 'method': 'mutUniformInt', 'params': {'indpb': 0.05, 'low': low, 'up': up}},
            {'rate': 0.15, 'method': 'mutPolynomialBounded', 'params': {'indpb': 0.05, 'low': low, 'up': up, 'eta': 3}},
            {'rate': 0.15, 'method': 'mutFlipBit', 'params': {'indpb': 0.05}},
        ],
        "selection_methods": [
            {'method': 'selTournament', 'params': {'tournsize': 3}},
            {'method': 'selBest', 'params': {}},
            {'method': 'selRoulette', 'params': {}},
        ]
    }
    for param, values in params.items():
        results = {}
        key = param.split("_")[0]
        for value in values:
            config = {**base_config}
            config.update({key: value})
            eesopt = GAOptimizationStudy(EES_exe, EES_model, inputs, outputs)
            eesopt.set_decision_variables(decision_variables)
            eesopt.set_target_variable("EUF_sys", r"$ EUF_{sys} $")
            # eesopt.set_target_variable("psi_sys_1", r"$ \psi_{sys} $")
            # eesopt.set_target_variable("m_dot[38]", r"$ \dot{m}_{38} $")
            result = eesopt.execute_GA(config)
            results.update({
                result["run_ID"]: {
                    "best_target": result["best_target"],
                    "best_individual": result["best_individual"],
                    "generations": result["generations"],
                    "evolution_time": result["evolution_time"],
                    "config": result["config"],
                    "best_output": result["best_output"],
                }
            })
            del eesopt
        print(" ")
        print(f"Resultados de: {param}")
        targets = []
        for idx, result in results.items():
            print(f"ID: {idx} | {result['best_target']}")
            targets.append((idx, [v for _, v in result["best_target"].items()][0]))

        best_target = sorted(targets, key=lambda x: x[1], reverse=True)[0]
        print(f"Valor máximo >> ID: {best_target[0]} | Valor: {best_target[1]}")
        print(f"Config: \n {results[best_target[0]]}")

        json_filename = os.path.join(opt_analysis_folder, f"opt_{param}_analysis.json")
        with open(json_filename, 'w') as jsonfile:
            json.dump(results, jsonfile)
        r_json_filename = os.path.join(opt_analysis_folder, f"opt_{param}_readable_analysis.json")
        with open(r_json_filename, 'w') as jsonfile:
            json.dump(results, jsonfile, indent=4)
        break


if __name__ == "__main__":
    EES_exe = r'C:\Root\Universidade\EES\EES.exe'
    EES_model = r'C:\Root\Universidade\Mestrado\Dissertação\Analises\models\trigeracao_LiBrH2O.EES'

    inputs = {
        'm_dot[9]': 0.0226,
        'T[1]': 25,
        'T[3]': 468,
        'T[4]': 763.4,
        'T[9]': 25,
        'eta_compressor': 0.85,
        'eta_turbina': 0.85,
        'rp': 3.22,
        'X_biogas_ch4': 0.6,
        'DeltaTmin': 10,
        'x[18]': 0,
        'Q_evaporador': 12,
        'epsilon_hx': 0.80,
        'eta_bomba': 0.95,
        'T[10]': 35,
        'T[13]': 85,
        'T[19]': 40,
        'T[22]': 5,
        'T[24]': 25,
        'T[25]': 30,
        'T[30]': 16,
        'T[31]': 10,
        'T[32]': 25,
        'T[34]': 80,
        'salinity': 3.535,
        'epsilon_u': 0.85,
        'epsilon_d': 0.85,
        'phi[36]': 0.9,
        'phi[37]': 0.9,
        'MR': 2.5,
        'T_0': 25,
        'P_0': 101.325
    }
    outputs = ['W_compressor', 'W_turbina', 'W_net', 'eta_brayton', 'Q_gerador', 'Q_absorvedor', 'Q_condensador', 'Q_evaporador',
               'UA_gerador', 'UA_absorvedor', 'UA_condensador', 'UA_evaporador', 'COP_1', 'COP_2', 'v_dot[38]', 'v_dot[32]',
               'm_dot[38]', 'm_dot[32]', 'Q_aquecedor', 'UA_aquecedor', 'RR', 'GOR', 'EUF_sys', 'Exd_compressor', 'psi_compressor',
               'Exd_regenerador', 'psi_regenerador', 'Exd_cc', 'psi_cc', 'Exd_turbina', 'psi_turbina', 'Exd_brayton', 'psi_brayton',
               'Exd_absorvedor', 'psi_absorvedor', 'Exd_gerador', 'psi_gerador', 'Exd_condensador', 'psi_condensador', 'Exd_evaporador',
               'psi_evaporador', 'Exd_vs', 'psi_vs', 'Exd_vr', 'psi_vr', 'Exd_hx', 'psi_hx', 'Exd_bomba', 'psi_bomba', 'psi_sra',
               'Exd_sra', 'Exd_umidificador', 'psi_umidificador', 'Exd_desumidificador', 'psi_desumidificador', 'Exd_aquecedor',
               'psi_aquecedor', 'Exd_hdh', 'psi_hdh', 'psi_sys_1', 'psi_sys_2', 'Exd_sys', 'delta_compressor', 'delta_regenerador',
               'delta_cc', 'delta_turbina', 'delta_absorvedor', 'delta_bomba', 'delta_vs', 'delta_vr', 'delta_hx', 'delta_gerador',
               'delta_condensador', 'delta_evaporador', 'delta_umidificador', 'delta_desumidificador', 'delta_aquecedor',
               'EUF_sys_turbina', 'EUF_sys_sra', 'EUF_sys_hdh', 'psi_sys_turbina', 'psi_sys_sra', 'psi_sys_hdh']

    decision_variables = {
        'm_dot[9]': (0.005, 0.035),
        'T[10]': (35, 44),
        'T[19]': (35, 48),
        'T[13]': (75, 90),
        'T[22]': (1, 6),
        'MR': (0.5, 4.5),
        'T[34]': (68, 100),
        'T[32]': (15, 40)
    }

    base_config = {
        'seed': 5,
        'population': 50,
        'crossover': {'rate': 0.5, 'method': 'cxTwoPoint', 'params': {}},
        'mutation': {'rate': 0.15, 'method': 'mutFlipBit', 'params': {'indpb': 0.05}},
        'selection': {'method': 'selTournament', 'params': {'tournsize': 3}},
        'max_generation': 40,
        'cvrg_tolerance': 1e-5
    }
    main(EES_exe, EES_model, inputs, outputs, decision_variables, base_config)
    # param_analysis(EES_exe, EES_model, inputs, outputs, decision_variables, base_config)
