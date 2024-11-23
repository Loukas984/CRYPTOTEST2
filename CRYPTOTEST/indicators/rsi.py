
import numpy as np
from indicators.base_indicator import BaseIndicator

class RSI(BaseIndicator):
    def __init__(self, period=14):
        super().__init__()
        self.period = period

    def calculate(self, data):
        close_prices = np.array(data)
        deltas = np.diff(close_prices)
        seed = deltas[:self.period+1]
        up = seed[seed >= 0].sum()/self.period
        down = -seed[seed < 0].sum()/self.period
        rs = up/down
        rsi = np.zeros_like(close_prices)
        rsi[:self.period] = 100. - 100./(1. + rs)

        for i in range(self.period, len(close_prices)):
            delta = deltas[i - 1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(self.period-1) + upval)/self.period
            down = (down*(self.period-1) + downval)/self.period
            rs = up/down
            rsi[i] = 100. - 100./(1. + rs)

        return rsi

    def get_signal(self, data, overbought=70, oversold=30):
        rsi_values = self.calculate(data)
        last_rsi = rsi_values[-1]

        if last_rsi > overbought:
            return 'SELL'
        elif last_rsi < oversold:
            return 'BUY'
        else:
            return 'NEUTRAL'
