import argparse
from typing import Any, Dict, Optional


class Config:

    storage: Dict[str, Any]

    def __init__(self):
        self.storage = {}

    def load_from_parser(self, parser: argparse.ArgumentParser):
        args = parser.parse_args()
        for key in vars(args):
            self.set(key, getattr(args, key))

    def _load_dotenv(self):
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ModuleNotFoundError:
            print('python-dotenv module not found! cannot load .env file.')
            pass

    def load(self):
        self._load_dotenv()

    def get(self, key: str, default: Any = None) -> Optional[Any]:
        if key not in self.storage:
            return default
        
        return self.storage[key]

    def set(self, key: str, value: Any):
        print(f'[Config] {key}={value}')
        self.storage[key] = value


config = Config()