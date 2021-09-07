import os
import sys
import math
import time
import logging
import win32ui
import dde
import pyautogui
import pyperclip
import subprocess
import pandas as pd
from icecream import ic
from rich import print
from .parametric import NoModelError


class OptimizationStudy:

    def __init__(self, EES_exe, EES_model, base_case_inputs, outputs):
        self.EES_exe = EES_exe
        self.EES_model = OptimizationStudy.check_model_path(EES_model)
        self.base_case_inputs = base_case_inputs
        self.outputs = outputs
        self.paths = self.set_paths()
        self.runID = round(time.time())
        self.logger = self.setup_logging()
        self.consecutive_error_count = 0
        self.is_ready = {
            'target_variable': False,
            'decision_variables': False,
            'DDE': False,
            'optimizer': False
        }

    def check_is_ready(self):
        if not all(value == True for value in self.is_ready.values()):
            raise Exception("Algo de errado ocorreu!")

    def set_paths(self):
        model_folder = os.path.dirname(self.EES_model)
        model_filename = os.path.basename(self.EES_model)
        base_folder = os.path.join(
            model_folder,
            '.'.join(model_filename.split('.')[:-1])
        )
        paths = {
            "plots": os.path.join(base_folder, ".optPlots"),
            "logs": os.path.join(base_folder, ".optLogs"),
            "results": os.path.join(base_folder, ".optResults")
        }
        # Check if folders exists and if not, creates them.
        for _, path in paths.items():
            if not os.path.exists(path):
                os.makedirs(path)

        return paths

    def set_target_variable(self, target_variable, target_variable_display=""):
        self.target_variable = target_variable
        self.target_variable_display = target_variable_display
        self.is_ready['target_variable'] = True

    def set_decision_variables(self, decision_variables):
        """Adds the decision variables dict as a attribute of the class."""
        self.decision_variables = decision_variables
        self.is_ready['decision_variables'] = True

    def setup_DDE(self):
        if "EES.exe" in str(subprocess.check_output('tasklist')):
            self.log(">> Uma instância do EES foi encontrada aberta. Ela será fechada.")
            os.system("taskkill /f /im  EES.exe")

        self.log(f">> Abrindo o EES em {self.EES_exe}")
        subprocess.Popen([self.EES_exe, '/hide'], shell=True, close_fds=True).pid
        time.sleep(15)
        self.server = dde.CreateServer()
        self.server.Create("PyhtonDDExyUiosdjU")

        self.connector = dde.CreateConversation(self.server)
        self.connector.ConnectTo("EES", "DDE")

        self.log(f">> Abrindo modelo {self.EES_model}")
        self.connector.Exec(f"[Open {self.EES_model}]")
        self.connector.Exec(f"[HideWindow ErrorMessages]")
        self.connector.Exec(f"[HideWindow WarningMessages]")

        self.is_ready['DDE'] = True

    def close(self):
        self.log(">> Fechando o EES")
        self.connector.Exec("[QUIT]")
        self.server.Shutdown()
        time.sleep(10)

    def eval_EES_model(self, individual):
        # Remove 0 and negative values from decision variables
        for i, (variable, limits) in enumerate(zip(individual, self.decision_variables.values())):
            if variable <= 0:
                individual[i] = (limits[0] + limits[1]) / 2

        try:
            self.prepare_inputs(individual)
            self.connector.Exec('[SOLVE]')
            target_variable = self.get_output()
            self.consecutive_error_count = 0
        except dde.error:
            self.consecutive_error_count += 1
            self.log(f">> Erro: Conexão DDE falhou. A variável target para esta rodada será considerado 0.")
            if self.consecutive_error_count > 2:
                self.log(">> O erro persiste. Reiniciando o EES.")
                try:
                    self.server.Shutdown()
                    os.system("taskkill /f /im  EES.exe")
                    del self.connector
                    del self.server
                except Exception as deletion_exception:
                    self.logger.exception(deletion_exception)

                self.setup_DDE()
                self.consecutive_error_count = 0
            target_variable = 0
        return (target_variable, )

    def prepare_inputs(self, individual):
        new_inputs = {}
        new_inputs.update(self.base_case_inputs)
        for (variable, _), ind_variable_value in zip(self.decision_variables.items(), individual):
            new_inputs.update({variable: ind_variable_value})

        input_chunks = OptimizationStudy.variable_dict_splitter(new_inputs, (254 - 35))
        for chunk in input_chunks:
            input_variables = " ".join([str(v) for v in chunk.keys()])
            input_values = " ".join([str(v) for v in chunk.values()])
            pyperclip.copy(input_values)
            self.connector.Exec(f"[Import \'Clipboard\' {input_variables}]")
            self.connector.Exec(f"[ClearClipboard]")

    def get_output(self):
        output_chunks = OptimizationStudy.variable_list_splitter(self.outputs, (254 - 35))
        results = []
        error_has_ocorred = False
        for chunk in output_chunks:
            output_variables = " ".join([str(var) for var in chunk])
            self.connector.Exec(f"[Export \'Clipboard\' {output_variables}]")
            result = pyperclip.paste()
            self.connector.Exec(f"[ClearClipboard]")
            pyperclip.copy('')

            result = result.replace("\t", " ").replace("\r\n", " ")
            results.extend(result.split(" "))

        self.output_dict = {}
        for output, result in zip(self.outputs, results):
            try:
                value = float(result)
            except ValueError:
                value = 0
                error_has_ocorred = True
            self.output_dict.update({output: value})

        if error_has_ocorred:
            self.log(">> Erro: O EES não exportou valores corretos. Variável target será 0.")
            self.output_dict.update({self.target_variable: 0})

        return self.output_dict[self.target_variable]

    def setup_logging(self):
        logfolder = self.paths['logs']
        if not os.path.exists(logfolder):
            os.makedirs(logfolder)

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s:%(filename)s:%(message)s')

        file_handler = logging.FileHandler(
            os.path.join(
                logfolder,
                f'{self.runID}_{self.__class__.__name__}.log'
            ))
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        return logger

    def log(self, text, only_log=True):
        print(text)
        if only_log:
            self.logger.info(text)

    @staticmethod
    def variable_dict_splitter(d, max_len):
        l = d.keys()
        len_of_l = len(" ".join(l))
        num_of_chunks = math.ceil(len_of_l / max_len)
        chunk_size = math.ceil(len_of_l / num_of_chunks)

        chunks = []
        chunk = []
        for variable in l:
            chunk.append(variable)
            if len(" ".join(chunk)) >= chunk_size:
                chunks.append({var: d[var] for var in chunk})
                chunk = []
        else:
            chunks.append({var: d[var] for var in chunk})

        return chunks

    @staticmethod
    def variable_list_splitter(l, max_len):
        len_of_l = len(" ".join(l))
        num_of_chunks = math.ceil(len_of_l / max_len)
        chunk_size = math.ceil(len_of_l / num_of_chunks)

        chunks = []
        chunk = []
        for variable in l:
            chunk.append(variable)
            if len(" ".join(chunk)) >= chunk_size:
                chunks.append(chunk)
                chunk = []
        else:
            chunks.append(chunk)
        return chunks

    @staticmethod
    def check_model_path(path):
        """Check if model path is absolute and check if file exists."""

        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)

        if not os.path.exists(path):
            raise NoModelError("The model does not exist in the path provided.")

        return path
