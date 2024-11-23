
from typing import Dict, Any
import time

class DataCache:
    def __init__(self, max_size: int = 1000, expiration_time: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.expiration_time = expiration_time

    def get(self, key: str) -> Any:
        if key in self.cache:
            item = self.cache[key]
            if time.time() - item['timestamp'] < self.expiration_time:
                return item['data']
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: Any):
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache, key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]

        self.cache[key] = {
            'data': value,
            'timestamp': time.time()
        }

    def clear(self):
        self.cache.clear()

    def remove(self, key: str):
        if key in self.cache:
            del self.cache[key]

    def get_size(self) -> int:
        return len(self.cache)

    def get_keys(self) -> list:
        return list(self.cache.keys())

    def is_expired(self, key: str) -> bool:
        if key in self.cache:
            return time.time() - self.cache[key]['timestamp'] >= self.expiration_time
        return True

    def refresh(self, key: str):
        if key in self.cache:
            self.cache[key]['timestamp'] = time.time()

    def get_stats(self) -> Dict[str, Any]:
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'expiration_time': self.expiration_time,
            'oldest_item_age': max([time.time() - item['timestamp'] for item in self.cache.values()]) if self.cache else 0,
            'newest_item_age': min([time.time() - item['timestamp'] for item in self.cache.values()]) if self.cache else 0
        }
