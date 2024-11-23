
from abc import ABC, abstractmethod
import logging

class BaseStrategy(ABC):
    def __init__(self, config, exchange_data, historical_data, portfolio):
        self.config = config
        self.exchange_data = exchange_data
        self.historical_data = historical_data
        self.portfolio = portfolio
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def analyze(self, symbol, timeframe):
        '''
        Analyse les données de marché et renvoie un signal de trading.
        '''
        pass

    @abstractmethod
    async def generate_signal(self, analysis_result):
        '''
        Génère un signal de trading basé sur l'analyse.
        '''
        pass

    async def execute(self, symbol, timeframe):
        '''
        Exécute la stratégie pour un symbole et un timeframe donnés.
        '''
        analysis_result = await self.analyze(symbol, timeframe)
        signal = await self.generate_signal(analysis_result)
        return signal

    def get_parameter(self, name, default=None):
        '''
        Récupère un paramètre de configuration de la stratégie.
        '''
        return self.config.get(name, default)

    def log_info(self, message):
        '''
        Enregistre un message d'information.
        '''
        self.logger.info(message)

    def log_error(self, message):
        '''
        Enregistre un message d'erreur.
        '''
        self.logger.error(message)

    def validate_parameters(self):
        '''
        Valide les paramètres de la stratégie.
        '''
        # À implémenter dans les classes filles si nécessaire
        pass
