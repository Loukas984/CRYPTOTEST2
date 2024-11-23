
import pandas as pd
from typing import Dict, Any
import os
import json
from datetime import datetime, timedelta

class HistoricalData:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def save_data(self, symbol: str, timeframe: str, data: pd.DataFrame):
        filename = f"{symbol}_{timeframe}.csv"
        filepath = os.path.join(self.data_dir, filename)
        data.to_csv(filepath, index=True)

    def load_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        filename = f"{symbol}_{timeframe}.csv"
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            return pd.read_csv(filepath, index_col=0, parse_dates=True)
        return pd.DataFrame()

    def update_data(self, symbol: str, timeframe: str, new_data: pd.DataFrame):
        existing_data = self.load_data(symbol, timeframe)
        updated_data = pd.concat([existing_data, new_data]).drop_duplicates().sort_index()
        self.save_data(symbol, timeframe, updated_data)

    def get_missing_data_ranges(self, symbol: str, timeframe: str, start_date: datetime, end_date: datetime) -> list:
        data = self.load_data(symbol, timeframe)
        if data.empty:
            return [(start_date, end_date)]

        missing_ranges = []
        current_date = start_date

        while current_date < end_date:
            if current_date not in data.index:
                range_start = current_date
                while current_date < end_date and current_date not in data.index:
                    current_date += timedelta(minutes=1)  # Assume 1-minute timeframe, adjust as needed
                missing_ranges.append((range_start, current_date))
            else:
                current_date += timedelta(minutes=1)

        return missing_ranges

    def get_data_info(self) -> Dict[str, Any]:
        info = {}
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.csv'):
                symbol, timeframe = filename[:-4].split('_')
                data = pd.read_csv(os.path.join(self.data_dir, filename), index_col=0, parse_dates=True)
                info[f"{symbol}_{timeframe}"] = {
                    "start_date": data.index[0].strftime("%Y-%m-%d %H:%M:%S"),
                    "end_date": data.index[-1].strftime("%Y-%m-%d %H:%M:%S"),
                    "num_records": len(data)
                }
        return info
