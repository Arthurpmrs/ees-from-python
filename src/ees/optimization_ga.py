import os
import time
import math
import json
import datetime
import random
import win32ui
import dde
import pyperclip
import subprocess
import pandas as pd
from icecream import ic
from rich import print
from deap import base
from deap import creator
from deap import tools
from .parametric import NoModelError
from .optimization import OptimizationStudy


class GAOptimizationStudy(OptimizationStudy):

    def __init__(self, EES_exe, EES_model, base_case_inputs, outputs):
        super().__init__(EES_exe, EES_model, base_case_inputs, outputs)

    def feasible(self, individual):
        self.eval_EES_model(individual)
        check = []
        for _, value in self.output_dict.items():
            if value > 0:
                check.append(True)
            else:
                check.append(False)
        if all(value == True for value in check):
            return True
        return False

    def setup_optimizer(self, config):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        self.toolbox = base.Toolbox()

        attrs = []
        # Attribute generator
        for variable, limits in self.decision_variables.items():
            attr_name = f"attr_{variable}"
            self.toolbox.register(attr_name, random.uniform, limits[0], limits[1])
            attrs.append(getattr(self.toolbox, attr_name))

        # Structure initializers
        self.toolbox.register("individual", tools.initCycle, creator.Individual,
                              tuple(attrs), n=1)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        self.toolbox.register("evaluate", self.eval_EES_model)
        self.toolbox.register("mate", getattr(tools, config["crossover"]["method"]), **config["crossover"]["params"])
        self.toolbox.register("mutate", getattr(tools, config["mutation"]["method"]), **config["mutation"]["params"])
        self.toolbox.register("select", getattr(tools, config["selection"]["method"]), **config["selection"]["params"])
        self.toolbox.decorate("evaluate", tools.DeltaPenalty(self.feasible, 0))

        self.is_ready['optimizer'] = True

    def execute_GA(self, config):
        try:
            self.setup_DDE()
            self.setup_optimizer(config)
            self.check_is_ready()
            result = self.optimize(config)
            del creator.Individual
            del creator.FitnessMax
        finally:
            self.close()
        return result

    def optimize(self, config):
        """Genetic Algorithm optimization algorithm."""
        # Tempo inicial
        start_time = time.time()

        # Configuração da Seed
        random.seed(config["seed"])

        # Population
        pop_num = config["population"]
        pop = self.toolbox.population(pop_num)

        # Crossover and mutation rates
        CXPB = config["crossover"]["rate"]
        MUTPB = config["mutation"]["rate"]

        # Starting Evolution
        self.log("---- Início da evolução ----")
        # Evaluate the entire population
        # fitnesses = list(map(self.toolbox.evaluate, pop))
        fitnesses = []
        for i, ind in enumerate(pop):
            result = self.toolbox.evaluate(ind)
            print(f"Nº: {i + 1} | {self.target_variable}: {result[0]}")
            print(f"Ind: {[f'{i:.4f}' for i in ind]}")
            fitnesses.append(result)

        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit

        self.log(f"Calculados {len(pop)} indivíduos")

        # Extracting all the fitnesses of
        fits = [ind.fitness.values[0] for ind in pop]

        # Variable keeping track of the number of generations
        g = 0
        gen_history = []
        fits_old = 0
        max_same_target_count = 5
        same_target_count = 0

        # Begin the evolution
        while g < config["max_generation"]:
            # A new generation
            g += 1
            self.log(" ")
            self.log(f"------- Geração {g} -------")

            # Select the next generation individuals
            offspring = self.toolbox.select(pop, len(pop))
            # Clone the selected individuals
            offspring = list(map(self.toolbox.clone, offspring))

            # Apply crossover on the offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                # cross two individuals with probability CXPB
                if random.random() < CXPB:
                    self.toolbox.mate(child1, child2)
                    # fitness values of the children
                    # must be recalculated later
                    del child1.fitness.values
                    del child2.fitness.values

            # Apply mutation on the offspring
            for mutant in offspring:
                # mutate an individual with probability MUTPB
                if random.random() < MUTPB:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            # fitnesses = map(self.toolbox.evaluate, invalid_ind)
            fitnesses = []
            for i, ind in enumerate(invalid_ind):
                result = self.toolbox.evaluate(ind)
                print(f"Nº: {i + 1} | {self.target_variable}: {result[0]}")
                print(f"Ind: {[f'{i:.4f}' for i in ind]}")
                fitnesses.append(result)

            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            self.log(f"Calculados {len(invalid_ind)} indivíduos")

            # The population is entirely replaced by the offspring
            pop[:] = offspring

            # Gather all the fitnesses in one list and print the stats
            fits = [ind.fitness.values[0] for ind in pop]

            n_show = 15
            pop_best_inds = self.get_best_inds(pop, n_show)
            best_ind = tools.selBest(pop_best_inds, 1)[0]

            self.log(f"Somente mostrando os TOP {n_show} indivíduos:")

            pop_list = []
            for ind in pop:
                target, variables = self.ind_to_dict(ind)
                variables = {k: round(v, 4) for (k, v) in variables.items()}
                pop_list.append({**target, **variables})

            df = pd.DataFrame(pop_list)
            df = df.sort_values(by=self.target_variable, ascending=False).head(n_show)
            self.log(f"Indivíduos:\n{df}")

            # Error calculation
            error = abs(fits_old - max(fits))
            fits_old = max(fits)

            length = len(pop)
            mean = sum(fits) / length
            sum2 = sum(x * x for x in fits)
            std = abs(sum2 / length - mean ** 2) ** 0.5

            print(" ")
            self.log("Estatísticas da geração:")
            self.log(f'Err: {error:.5f}')
            self.log(f"Min: {min(fits):.5f}")
            self.log(f"Max: {max(fits):.5f}")
            self.log(f"Avg: {mean:.5f}")
            self.log(f"Std: {std:.5f}")

            self.eval_EES_model(best_ind)
            gen_history.append({
                "best_target": best_ind.fitness.values[0],
                "best_individual": best_ind,
                "error": error,
                "stats": {
                    "min": min(fits),
                    "max": max(fits),
                    "avg": mean,
                    "std": std
                },
                "best_output": self.output_dict
            })

            # Critério de convergência
            if error < config["cvrg_tolerance"]:
                same_target_count += 1
                if same_target_count > max_same_target_count:
                    self.log(f">> Critério de convergência atingido na geração {g}")
                    break
            else:
                same_target_count = 0

        self.log("---- Fim da evolução ----")
        delta_t = time.time() - start_time
        target, variables = self.ind_to_dict(best_ind)
        results = {
            "run_ID": self.runID,
            "best_target": target,
            "best_individual": variables,
            "evolution_time": delta_t,
            "generations": g,
            "config": config,
            "best_output": gen_history[-1]["best_output"],
            "gen_history": gen_history,
        }

        self.display_results(results)
        self.save_to_json(results, "results")
        return results

    def save_to_json(self, results, filename):
        with open(os.path.join(self.paths["results"], f"{self.runID}_{filename}.json"), "w") as jsonfile:
            json.dump(results, jsonfile)
        with open(os.path.join(self.paths["results"], f"{self.runID}_readable-{filename}.json"), "w") as jsonfile:
            json.dump(results, jsonfile, indent=4)

    def ind_to_dict(self, ind):
        target = {
            self.target_variable: ind.fitness.values[0]
        }

        variables = {}
        for variable, value in zip(self.decision_variables.keys(), ind):
            variables.update({variable: value})

        return target, variables

    def get_best_inds(self, pop, size):
        tuple_list = [(ind, ind.fitness.values[0]) for ind in pop]
        ordered_list = sorted(tuple_list, key=lambda x: x[1], reverse=True)
        return [ind for ind, fitness in ordered_list[:size]]

    def display_results(self, results):
        self.log(f"Run ID: {self.runID}")
        self.log(f"Tempo de Execução: {datetime.timedelta(seconds=results['evolution_time'])}")
        self.log(f"Melhor valor da função objetivo:")
        self.log(results["best_target"])
        self.log(f"Melhor Indivíduo (Conjunto de variáveis de decisão):")
        self.log({k: round(v, 4) for (k, v) in results["best_individual"].items()})
        self.log(f"Parâmetros do Algoritmo Genético:")
        self.log(results["config"])
        self.log("Output referente ao melhor indivíduo: ")
        self.log({k: round(v, 4) for (k, v) in results["best_output"].items()})