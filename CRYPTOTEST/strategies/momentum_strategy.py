
from strategies.base_strategy import BaseStrategy
from indicators.macd import MACD
from indicators.adx import ADX

class MomentumStrategy(BaseStrategy):
    def __init__(self, symbol, timeframe='15m', macd_fast=12, macd_slow=26, macd_signal=9, adx_period=14, adx_threshold=25):
        super().__init__(symbol, timeframe)
        self.macd = MACD(fast_period=macd_fast, slow_period=macd_slow, signal_period=macd_signal)
        self.adx = ADX(period=adx_period)
        self.adx_threshold = adx_threshold
        
    def generate_signals(self, data):
        close_prices = [candle['close'] for candle in data]
        high_prices = [candle['high'] for candle in data]
        low_prices = [candle['low'] for candle in data]
        
        macd_line, signal_line, _ = self.macd.calculate(close_prices)
        adx_values = self.adx.calculate(high_prices, low_prices, close_prices)
        
        signals = []
        
        # Conditions d'entrée
        if macd_line[-1] > signal_line[-1] and macd_line[-2] <= signal_line[-2] and adx_values[-1] > self.adx_threshold:
            signals.append({
                'type': 'BUY',
                'symbol': self.symbol,
                'price': close_prices[-1],
                'timestamp': data[-1]['timestamp'],
                'metadata': {
                    'macd': macd_line[-1],
                    'signal': signal_line[-1],
                    'adx': adx_values[-1]
                }
            })
        elif macd_line[-1] < signal_line[-1] and macd_line[-2] >= signal_line[-2] and adx_values[-1] > self.adx_threshold:
            signals.append({
                'type': 'SELL',
                'symbol': self.symbol,
                'price': close_prices[-1],
                'timestamp': data[-1]['timestamp'],
                'metadata': {
                    'macd': macd_line[-1],
                    'signal': signal_line[-1],
                    'adx': adx_values[-1]
                }
            })
        
        return signals

    def calculate_position_size(self, account_balance, risk_per_trade):
        # Implement position sizing logic based on account balance and risk per trade
        return min(account_balance * risk_per_trade, account_balance * 0.02)  # Max 2% of account balance per trade

    def set_stop_loss(self, entry_price, position_type):
        # Implement dynamic stop-loss calculation
        return entry_price * (0.98 if position_type == 'LONG' else 1.02)  # 2% stop-loss

    def set_take_profit(self, entry_price, position_type):
        # Implement dynamic take-profit calculation
        return entry_price * (1.04 if position_type == 'LONG' else 0.96)  # 4% take-profit
