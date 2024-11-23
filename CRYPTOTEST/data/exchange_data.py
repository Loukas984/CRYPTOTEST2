
import ccxt
import pandas as pd
from datetime import datetime, timedelta

class ExchangeData:
    def __init__(self, exchange_name, api_key, api_secret):
        self.exchange = getattr(ccxt, exchange_name)({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })
        self.data = {}
        self.current_timestamp = None
        self.trading_pairs = []

    def set_trading_pairs(self, pairs):
        self.trading_pairs = pairs
        for pair in pairs:
            if pair not in self.data:
                self.data[pair] = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                self.data[pair].set_index('timestamp', inplace=True)

    def load_historical_data(self, symbol, start_date, end_date, timeframe='1m'):
        since = int(start_date.timestamp() * 1000)
        end = int(end_date.timestamp() * 1000)
        
        all_ohlcv = []
        while since < end:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since)
            if len(ohlcv) == 0:
                break
            all_ohlcv.extend(ohlcv)
            since = ohlcv[-1][0] + 1
        
        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        self.data[symbol] = df

    def update(self):
        if self.current_timestamp is None:
            self.current_timestamp = datetime.now()
        
        for symbol in self.data.keys():
            latest_data = self.exchange.fetch_ohlcv(symbol, '1m', limit=1)
            if latest_data:
                latest_df = pd.DataFrame(latest_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                latest_df['timestamp'] = pd.to_datetime(latest_df['timestamp'], unit='ms')
                latest_df.set_index('timestamp', inplace=True)
                self.data[symbol] = self.data[symbol].append(latest_df)
        
        self.current_timestamp = datetime.now()

    def update_to_timestamp(self, timestamp):
        self.current_timestamp = timestamp
        for symbol in self.data.keys():
            self.data[symbol] = self.data[symbol][self.data[symbol].index <= timestamp]

    def get_data(self, symbol):
        return self.data.get(symbol)

    def get_latest_price(self, symbol):
        df = self.data.get(symbol)
        if df is not None and not df.empty:
            return df['close'].iloc[-1]
        return None

    def get_total_value(self, portfolio):
        total_value = portfolio.balance
        for symbol, amount in portfolio.positions.items():
            latest_price = self.get_latest_price(symbol)
            if latest_price is not None:
                total_value += amount * latest_price
        return total_value

    def get_market_value(self, symbol):
        df = self.data.get(symbol)
        if df is not None and not df.empty:
            return df['close'].iloc[-1]
        return None

class MockExchange:
    def __init__(self):
        self.id = 'mock'
        self.apiKey = 'mock_api_key'
        self.secret = 'mock_secret'

    def fetch_ohlcv(self, symbol, timeframe, since):
        import numpy as np
        dates = pd.date_range(start=datetime.fromtimestamp(since/1000), periods=100, freq=timeframe)
        close_prices = np.random.randint(30000, 40000, size=100)
        return [[int(d.timestamp() * 1000), 0, 0, 0, p, 0] for d, p in zip(dates, close_prices)]

class MockExchangeData(ExchangeData):
    def __init__(self):
        self.exchange = MockExchange()
        self.data = {}
        self.current_timestamp = None
        self.trading_pairs = []

    def set_trading_pairs(self, pairs):
        self.trading_pairs = pairs
        for pair in pairs:
            if pair not in self.data:
                self.data[pair] = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                self.data[pair].set_index('timestamp', inplace=True)

    def load_historical_data(self, symbol, start_date, end_date, timeframe='1d'):
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, int(start_date.timestamp() * 1000))
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        self.data[symbol] = df

    def update_to_timestamp(self, timestamp):
        self.current_timestamp = timestamp
        for symbol in self.data.keys():
            self.data[symbol] = self.data[symbol][self.data[symbol].index <= timestamp]

    def get_latest_price(self, symbol):
        df = self.data.get(symbol)
        if df is not None and not df.empty:
            return df['close'].iloc[-1]
        return None
