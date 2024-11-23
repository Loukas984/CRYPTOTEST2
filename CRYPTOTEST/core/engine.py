
import asyncio
from typing import Dict, List
from core.exchange_handler import ExchangeHandler
from core.plugin_manager import PluginManager
from data.exchange_data import ExchangeData
from data.historical_data import HistoricalData
from portfolio_management.portfolio import Portfolio
from portfolio_management.risk_management import RiskManager
from utils.logging_config import setup_logging

class TradingEngine:
    def __init__(self, config: Dict):
        self.logger = setup_logging()
        self.config = config
        self.exchange_handler = ExchangeHandler(config['exchange'])
        self.plugin_manager = PluginManager()
        self.exchange_data = ExchangeData(self.exchange_handler)
        self.historical_data = HistoricalData(self.exchange_handler)
        self.portfolio = Portfolio(config['initial_balance'])
        self.risk_manager = RiskManager(config['risk_params'])
        self.strategies = []
        self.running = False

    async def start(self):
        self.logger.info("Starting trading engine...")
        self.running = True
        await self.load_strategies()
        await asyncio.gather(
            self.update_market_data(),
            self.run_strategies()
        )

    async def stop(self):
        self.logger.info("Stopping trading engine...")
        self.running = False

    async def load_strategies(self):
        for strategy_config in self.config['strategies']:
            strategy = self.plugin_manager.load_strategy(strategy_config['name'])
            strategy.initialize(strategy_config['params'])
            self.strategies.append(strategy)

    async def update_market_data(self):
        while self.running:
            try:
                await self.exchange_data.update()
                await asyncio.sleep(self.config['update_interval'])
            except Exception as e:
                self.logger.error(f"Error updating market data: {e}")

    async def run_strategies(self):
        while self.running:
            for strategy in self.strategies:
                try:
                    signals = strategy.generate_signals(self.exchange_data.get_latest_data())
                    for signal in signals:
                        if self.risk_manager.check_risk(signal, self.portfolio):
                            order = await self.execute_trade(signal)
                            if order:
                                self.portfolio.update(order)
                except Exception as e:
                    self.logger.error(f"Error in strategy {strategy.name}: {e}")
            await asyncio.sleep(self.config['strategy_interval'])

    async def execute_trade(self, signal: Dict) -> Dict:
        try:
            order = await self.exchange_handler.place_order(
                symbol=signal['symbol'],
                side=signal['type'],
                amount=self.risk_manager.calculate_position_size(signal, self.portfolio),
                price=signal['price']
            )
            self.logger.info(f"Executed trade: {order}")
            return order
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return None

    def get_performance_metrics(self):
        return self.portfolio.get_metrics()

if __name__ == "__main__":
    # Example configuration
    config = {
        'exchange': {'name': 'binance', 'api_key': 'your_api_key', 'secret_key': 'your_secret_key'},
        'initial_balance': 10000,
        'risk_params': {'max_position_size': 0.02, 'stop_loss_pct': 0.01, 'take_profit_pct': 0.03},
        'strategies': [
            {'name': 'ScalpingStrategy', 'params': {'rsi_period': 14, 'rsi_overbought': 70, 'rsi_oversold': 30}},
            {'name': 'MomentumStrategy', 'params': {'ema_fast': 12, 'ema_slow': 26, 'macd_signal': 9}}
        ],
        'update_interval': 1,  # seconds
        'strategy_interval': 5  # seconds
    }

    engine = TradingEngine(config)
    asyncio.run(engine.start())
