import os
import sys
sys.path.append(os.path.join(os.getcwd(), 'src'))
import numpy as np
import pandas as pd
from ees.parametric import ParametricStudies
from graphs_analise_dolar import DollarAnalisys

EES_exe = r'C:\Root\Universidade\EES\EES.exe'
# EES_exe = r'C:\Root\Universidade\EES_antigo\EES.exe'
EES_model = r'C:\Root\Drive\Unicamp\[Unicamp]\[Dissertação]\01 - Algoritmo\Analise Economica\Cálculos\trigeracao_LiBrH2O_economic_py.EES'

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
    'P_0': 101.325,
    'dolar': 5.50,
    'tarifa_energia_eletrica': 0.62,
    'custo_agua': 13,
    'ir': 0.15
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
           'EUF_sys_turbina', 'EUF_sys_sra', 'EUF_sys_hdh', 'psi_sys_turbina', 'psi_sys_sra', 'psi_sys_hdh', 'payback_simples_1',
           'payback_simples_2', 'payback_simples_3', 'cost_CAPEX_2019_real_trigen', 'cost_OPEX_real_anual', 'cost_prod',
           'cost_CAPEX_2019_real_total', 'cost_op_MR', 'cost_op_PR', 'cost_op_D', 'cost_op_IS', 'cost_op_DA']

parametric_inputs = {
    'dolar': np.linspace(3, 6, 20)
}

# eesmodel = ParametricStudies(EES_exe, EES_model, inputs, parametric_inputs, outputs)
# parametric_table = eesmodel.execute()

# for variable, df in parametric_table.items():
#     print(df)

graph = DollarAnalisys(EES_model)
graph.generate(lang='en-US')
graph.generate(lang='pt-BR')
