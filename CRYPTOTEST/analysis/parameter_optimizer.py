
import random
import numpy as np
from deap import base, creator, tools, algorithms
from analysis.backtester import Backtester
from utils.logging_config import setup_logging

class ParameterOptimizer:
    def __init__(self, strategy_class, historical_data, initial_balance, risk_params):
        self.logger = setup_logging()
        self.strategy_class = strategy_class
        self.historical_data = historical_data
        self.initial_balance = initial_balance
        self.risk_params = risk_params

    def evaluate(self, individual):
        # Convert the individual to a dictionary of parameters
        params = dict(zip(self.param_names, individual))
        
        # Create a strategy instance with these parameters
        strategy = self.strategy_class(**params)
        
        # Run the backtester
        backtester = Backtester(strategy, self.initial_balance, self.risk_params)
        results = backtester.run(self.historical_data)
        
        # Return the negative of the total return (we want to maximize it)
        return -results['total_return'],

    def optimize(self, param_ranges, population_size=50, generations=50):
        self.param_names = list(param_ranges.keys())
        
        # Create types
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        # Initialize toolbox
        toolbox = base.Toolbox()
        for i, (param, (low, high)) in enumerate(param_ranges.items()):
            toolbox.register(f"attr_{i}", random.uniform, low, high)
        
        toolbox.register("individual", tools.initCycle, creator.Individual,
                         (getattr(toolbox, f"attr_{i}") for i in range(len(param_ranges))),
                         n=1)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        
        toolbox.register("evaluate", self.evaluate)
        toolbox.register("mate", tools.cxBlend, alpha=0.5)
        toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
        toolbox.register("select", tools.selTournament, tournsize=3)

        # Create initial population
        pop = toolbox.population(n=population_size)
        
        # Run the genetic algorithm
        algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=generations, verbose=False)
        
        # Get the best individual
        best_ind = tools.selBest(pop, 1)[0]
        best_params = dict(zip(self.param_names, best_ind))
        
        self.logger.info(f"Best parameters found: {best_params}")
        return best_params

if __name__ == "__main__":
    # Example usage
    from strategies.momentum_strategy import MomentumStrategy
    import pandas as pd

    # Load historical data (you would need to implement this)
    historical_data = pd.read_csv("path_to_your_historical_data.csv")

    optimizer = ParameterOptimizer(
        MomentumStrategy,
        historical_data,
        initial_balance=10000,
        risk_params={'max_position_size': 0.1}
    )

    param_ranges = {
        'ema_fast': (5, 20),
        'ema_slow': (20, 50),
        'macd_signal': (5, 20)
    }

    best_params = optimizer.optimize(param_ranges)
    print(f"Optimized parameters: {best_params}")
