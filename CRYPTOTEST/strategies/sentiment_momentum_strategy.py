
from strategies.base_strategy import BaseStrategy
from indicators.macd import MACD
from indicators.rsi import RSI
from analysis.sentiment_analysis import SentimentAnalyzer

class SentimentMomentumStrategy(BaseStrategy):
    def __init__(self, symbol, timeframe='1h', macd_fast=12, macd_slow=26, macd_signal=9, rsi_period=14, sentiment_threshold=0.2):
        super().__init__(symbol, timeframe)
        self.macd = MACD(fast_period=macd_fast, slow_period=macd_slow, signal_period=macd_signal)
        self.rsi = RSI(period=rsi_period)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.sentiment_threshold = sentiment_threshold

    def generate_signals(self, data):
        close_prices = [candle['close'] for candle in data]
        macd, signal, _ = self.macd.calculate(close_prices)
        rsi = self.rsi.calculate(close_prices)
        sentiment = self.sentiment_analyzer.get_overall_sentiment(self.symbol.split('/')[0])  # Assuming BTC/USDT format

        signals = []

        # MACD crossover
        if macd[-1] > signal[-1] and macd[-2] <= signal[-2]:
            # Bullish MACD crossover
            if rsi[-1] < 70 and sentiment > self.sentiment_threshold:
                signals.append({
                    'type': 'BUY',
                    'symbol': self.symbol,
                    'price': close_prices[-1],
                    'timestamp': data[-1]['timestamp'],
                    'metadata': {
                        'macd': macd[-1],
                        'signal': signal[-1],
                        'rsi': rsi[-1],
                        'sentiment': sentiment
                    }
                })
        elif macd[-1] < signal[-1] and macd[-2] >= signal[-2]:
            # Bearish MACD crossover
            if rsi[-1] > 30 and sentiment < -self.sentiment_threshold:
                signals.append({
                    'type': 'SELL',
                    'symbol': self.symbol,
                    'price': close_prices[-1],
                    'timestamp': data[-1]['timestamp'],
                    'metadata': {
                        'macd': macd[-1],
                        'signal': signal[-1],
                        'rsi': rsi[-1],
                        'sentiment': sentiment
                    }
                })

        return signals

    def calculate_position_size(self, account_balance, risk_per_trade):
        # Implement position sizing logic based on account balance and risk per trade
        return min(account_balance * risk_per_trade, account_balance * 0.02)  # Max 2% of account balance per trade

    def set_stop_loss(self, entry_price, position_type):
        # Implement dynamic stop-loss calculation
        return entry_price * (0.97 if position_type == 'LONG' else 1.03)  # 3% stop-loss

    def set_take_profit(self, entry_price, position_type):
        # Implement dynamic take-profit calculation
        return entry_price * (1.06 if position_type == 'LONG' else 0.94)  # 6% take-profit
