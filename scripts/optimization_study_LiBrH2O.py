import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'src'))
import json
import logging
import datetime
from rich import print
from icecream import ic
from ees.optimization import OptimizationStudy
from ees.optimization_ga import GAOptimizationStudy
from ees.optimization_graphs import OptGraph
from ees.utilities import get_base_folder, add_folder


def optimization(EES_exe, EES_model, inputs, outputs, decision_variables, base_config):
    """Run one optimization case."""
    eesopt = GAOptimizationStudy(EES_exe, EES_model, inputs, outputs)
    eesopt.set_decision_variables(decision_variables)
    eesopt.set_target_variable("EUF_sys", r"$ EUF_{sys} $")
    # eesopt.set_target_variable("psi_sys_1", r"$ \psi_{sys} $")
    # eesopt.set_target_variable("m_dot[38]", r"$ \dot{m}_{38} $")
    eesopt.execute_GA(base_config)
    graph = OptGraph(eesopt.paths["base_folder"])
    graph.generate(r"$ EUF_{sys} $", lang="pt-BR")
    graph.generate(r"$ EUF_{sys} $", lang="en-US")


def param_analysis(EES_exe, EES_model, inputs, outputs, decision_variables, base_config, params):
    base_folder = get_base_folder(EES_model)
    opt_analysis_folder = add_folder(base_folder, ".optAnalysis")

    target_variable = "EUF_sys"
    target_display = r"$ EUF_{sys} $"
    # target_variable = "psi_sys_1"
    # target_display = r"$ \psi_{sys} $"
    # target_variable = "m_dot[38]"
    # target_display = r"$ \dot{m}_{38} $"
    for param, values in params.items():
        results = {}
        key = param.split("_")[0]
        for i, value in enumerate(values):

            if value == None:
                continue

            config = {**base_config}
            config.update({key: value})

            print(" ")
            print("Iniciando nova análise com os seguintes valores:")
            print(value)

            filtered_result = {}
            eesopt = GAOptimizationStudy(EES_exe, EES_model, inputs, outputs)
            eesopt.set_decision_variables(decision_variables)
            eesopt.set_target_variable(target_variable, target_display)
            result = eesopt.execute_GA(config)
            if result == {}:
                results.update(result)
                continue

            filtered_result = {
                result["run_ID"]: {
                    "best_target": result["best_target"],
                    "best_individual": result["best_individual"],
                    "generations": result["generations"],
                    "evolution_time": result["evolution_time"],
                    "config": result["config"],
                    "best_output": result["best_output"],
                }
            }
            results.update(filtered_result)

            # Save run result to file
            folderpath = add_folder(opt_analysis_folder, target_variable, param)

            filename = f"result_run_{i + 1}.json"
            filepath = os.path.join(folderpath, filename)

            with open(filepath, 'w') as jsonfile:
                json.dump(filtered_result, jsonfile)

            filename_readable = f"result-readable_run_{i + 1}.json"
            filepath_readable = os.path.join(folderpath, filename_readable)

            with open(filepath_readable, 'w') as jsonfile:
                json.dump(filtered_result, jsonfile, indent=4)

            del eesopt


def get_best_result(EES_exe, EES_model, params):
    base_folder = get_base_folder(EES_model)
    opt_analysis_folder = add_folder(base_folder, ".optAnalysis")

    target_variable = "EUF_sys"
    target_display = r"$ EUF_{sys} $"
    # target_variable = "psi_sys_1"
    # target_display = r"$ \psi_{sys} $"
    # target_variable = "m_dot[38]"
    # target_display = r"$ \dot{m}_{38} $"
    target_variable_folder = os.path.join(opt_analysis_folder, target_variable)

    # Setup logging
    logfolder = os.path.join(opt_analysis_folder, target_variable)
    logger = setup_logging(logfolder)

    for param, values in params.items():
        folderpath = os.path.join(target_variable_folder, param)
        results = {}
        for i, value in enumerate(values):
            filename = f"result_run_{i + 1}.json"
            filepath = os.path.join(folderpath, filename)

            with open(filepath, 'r') as jsonfile:
                results.update(json.load(jsonfile))

        log(logger, f"Análise de: {param}")
        sorted_results = sorted(
            [(idx, r["best_target"][target_variable], v) for (idx, r), v in zip(results.items(), values)],
            key=lambda x: x[1],
            reverse=True
        )
        for result in sorted_results:
            log(logger, f"ID: {result[0]} | {target_variable}: {result[1]} | {param}: {result[2]}")

        best_result = results[sorted_results[0][0]]

        log(logger, f"Run ID: {sorted_results[0][0]}")
        log(logger, f"Tempo de Execução: {datetime.timedelta(seconds=best_result['evolution_time'])}")
        log(logger, f"Gerações para a convergência: {best_result['generations']}")
        log(logger, f"Melhor valor da função objetivo:")
        log(logger, best_result["best_target"])
        log(logger, f"Melhor Indivíduo (Conjunto de variáveis de decisão):")
        log(logger, {k: round(v, 4) for (k, v) in best_result["best_individual"].items()})
        log(logger, f"Parâmetros do Algoritmo Genético:")
        log(logger, best_result["config"])
        log(logger, "Output referente ao melhor indivíduo: ")
        log(logger, {k: round(v, 4) for (k, v) in best_result["best_output"].items()})
        log(logger, " ")


def log(logger, message):
    logger.info(message)
    print(message)


def setup_logging(logfolder):
    if not os.path.exists(logfolder):
        os.makedirs(logfolder)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s:%(filename)s:%(message)s')

    file_handler = logging.FileHandler(
        os.path.join(
            logfolder,
            f'best-results.log'
        ))
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


def main():
    EES_exe = r'C:\Root\Universidade\EES\EES.exe'
    EES_model = r'C:\Root\Universidade\Mestrado\Analise\trigeracao_LiBrH2O.EES'

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
        'T[10]': (35, 44),
        'T[19]': (35, 48),
        'T[13]': (75, 90),
        'T[22]': (1, 6),
        'MR': (0.5, 4.5),
        'T[34]': (68, 100),
        'T[32]': (15, 40)
    }

    low = tuple([v[0] for _, v in decision_variables.items()])
    up = tuple([v[1] for _, v in decision_variables.items()])

    mu = [(x2 - x1) / 5 for x1, x2 in decision_variables.values()]

    int_low = tuple([int(l) for l in low])
    int_up = tuple([int(u) for u in up])

    base_config = {
        'seed': 5,
        'population': 50,
        'crossover': {'rate': 0.5, 'method': 'cxTwoPoint', 'params': {}},
        'mutation': {'rate': 0.10, 'method': 'mutUniformInt', 'params': {'indpb': 0.05, 'low': int_low, 'up': int_up}},
        'selection': {'method': 'selTournament', 'params': {'tournsize': 5}},
        'max_generation': 150,
        'cvrg_tolerance': 1e-5,
        'verbose': True
    }

    best_config = {
        'seed': 5,
        'population': 150,
        'crossover': {'rate': 0.7, 'method': 'cxBlend', 'params': {'alpha': 0.4}},
        'mutation': {'rate': 0.2, 'method': 'mutPolynomialBounded', 'params': {'indpb': 0.05, 'low': low, 'up': up, 'eta': 3}},
        'selection': {'method': 'selStochasticUniversalSampling', 'params': {}},
        'max_generation': 150,
        'cvrg_tolerance': 1e-5,
        'verbose': True
    }

    params = {
        "population": [10, 15, 25, 50, 100, 150, 200],
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
            {'rate': 0.5, 'method': 'cxSimulatedBinaryBounded', 'params': {'eta': 3, 'low': low, 'up': up}},
            {'rate': 0.5, 'method': 'cxBlend', 'params': {'alpha': 0.4}}
        ],
        "mutation_rates": [
            {'rate': 0.05, 'method': 'mutUniformInt', 'params': {'indpb': 0.05, 'low': int_low, 'up': int_up}},
            {'rate': 0.10, 'method': 'mutUniformInt', 'params': {'indpb': 0.05, 'low': int_low, 'up': int_up}},
            {'rate': 0.15, 'method': 'mutUniformInt', 'params': {'indpb': 0.05, 'low': int_low, 'up': int_up}},
            {'rate': 0.20, 'method': 'mutUniformInt', 'params': {'indpb': 0.05, 'low': int_low, 'up': int_up}},
            {'rate': 0.25, 'method': 'mutUniformInt', 'params': {'indpb': 0.05, 'low': int_low, 'up': int_up}}
        ],
        "mutation_methods": [
            {'rate': 0.10, 'method': 'mutGaussian', 'params': {'indpb': 0.05, 'mu': mu, 'sigma': 0.15}},
            {'rate': 0.10, 'method': 'mutPolynomialBounded', 'params': {'indpb': 0.05, 'low': low, 'up': up, 'eta': 3}},
            {'rate': 0.10, 'method': 'mutUniformInt', 'params': {'indpb': 0.05, 'low': int_low, 'up': int_up}},
        ],
        "selection_methods": [
            {'method': 'selTournament', 'params': {'tournsize': 5}},
            {'method': 'selBest', 'params': {}},
            {'method': 'selRoulette', 'params': {}},
            {'method': 'selStochasticUniversalSampling', 'params': {}},
        ]
    }

    # optimization(EES_exe, EES_model, inputs, outputs, decision_variables, base_config)
    optimization(EES_exe, EES_model, inputs, outputs, decision_variables, best_config)
    # param_analysis(EES_exe, EES_model, inputs, outputs, decision_variables, base_config, params)
    # get_best_result(EES_exe, EES_model, params)


if __name__ == "__main__":
    main()
