import pandas as pd
from abc import ABCMeta, abstractmethod
from api import RestClient as rest_client
from api import LocalClient as local_client


class BaseETLAdapter(metaclass=ABCMeta):

    __slots__ = ('symbol', 'url', 'params', 'use_local_client')

    def __init__(self, symbol: str, url: str, params: dict = None, use_local_client: bool = False):
        assert url

        self.symbol = symbol
        self.url = url
        self.params = params or {}
        self.use_local_client = use_local_client

    @abstractmethod
    def transform(self, url: str, params: dict) -> pd.DataFrame:
        pass

    def run(self, save: bool = False) -> pd.DataFrame:
        dataframe = self.transform(url=self.url, params=self.params)
        if save:
            c = local_client if self.use_local_client else rest_client
            c.save(symbol=self.symbol, dataframe=dataframe)
            print(f'Symbol {self.symbol} saved successfully.')

        return dataframe
