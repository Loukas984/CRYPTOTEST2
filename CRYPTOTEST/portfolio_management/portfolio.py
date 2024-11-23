
from typing import Dict
import pandas as pd

class Portfolio:
    def __init__(self):
        self.positions: Dict[str, float] = {}
        self.balance: float = 0
        self.trade_history: list = []
        self.value_history: list = []

    def update_status(self, exchange_data):
        total_value = self.balance
        for symbol, amount in self.positions.items():
            latest_price = exchange_data.get_latest_price(symbol)
            if latest_price is not None:
                total_value += amount * latest_price
        self.trade_history.append({'timestamp': pd.Timestamp.now(), 'total_value': total_value})
        self.value_history.append(total_value)
        
    def execute_trade(self, signal):
        symbol = signal['symbol']
        amount = signal['amount']
        price = signal['price']
        if signal['action'] == 'buy':
            cost = amount * price
            if cost <= self.balance:
                self.positions[symbol] = self.positions.get(symbol, 0) + amount
                self.balance -= cost
            else:
                raise ValueError("Insufficient balance for this trade")
        elif signal['action'] == 'sell':
            current_position = self.positions.get(symbol, 0)
            if amount <= current_position:
                self.positions[symbol] = current_position - amount
                self.balance += amount * price
            else:
                raise ValueError("Insufficient position for this trade")
        self.trade_history.append({'timestamp': pd.Timestamp.now(), 'action': signal['action'], 'symbol': symbol, 'amount': amount, 'price': price})
        self.update_value_history()

    def get_position(self, symbol):
        return self.positions.get(symbol, 0)

    def get_balance(self):
        return self.balance

    def calculate_returns(self):
        if len(self.trade_history) < 2:
            return pd.Series()
        df = pd.DataFrame(self.trade_history)
        df.set_index('timestamp', inplace=True)
        returns = df['total_value'].pct_change()
        return returns.dropna()

    def get_total_value(self, exchange_data):
        total_value = self.balance
        for symbol, amount in self.positions.items():
            latest_price = exchange_data.get_latest_price(symbol)
            if latest_price is not None:
                total_value += amount * latest_price
        return total_value

    def calculate_drawdown(self):
        if not self.value_history:
            return 0
        peak = max(self.value_history)
        current_value = self.value_history[-1]
        return (peak - current_value) / peak

    def update_value_history(self):
        total_value = self.balance
        for symbol, amount in self.positions.items():
            # Assuming we have the latest price in the trade history
            latest_trade = next((trade for trade in reversed(self.trade_history) if trade['symbol'] == symbol), None)
            if latest_trade:
                total_value += amount * latest_trade['price']
        self.value_history.append(total_value)
