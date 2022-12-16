import numpy as np
import pandas as pd
from analytics.constants import FUTURES_DELIVERY_MAP
from market.etl_adapter import BaseETLAdapter


class CMEOptionExpiriesAdapter(BaseETLAdapter):

    def transform(self, url: str, params: dict) -> pd.DataFrame:
        assert url

        dataframe = pd.read_excel(
            url,
            skiprows=4
        )

        dataframe.index = [
            ''.join((product_code[2:3], '20', product_code[3:]))
            for product_code in dataframe['Product Code']
        ]
        dataframe = dataframe[['Settlement']]
        dataframe.columns = ['EXPIRATION_DATE']
        dataframe['EXPIRATION_DATE'] = dataframe['EXPIRATION_DATE'].astype(np.datetime64)

        return dataframe


class ICEOptionExpiriesAdapter(BaseETLAdapter):

    def transform(self, url: str, params: dict) -> pd.DataFrame:
        assert url

        dataframe = pd.read_csv(url)
        dataframe.index = [
            ''.join((FUTURES_DELIVERY_MAP[contract[2:5].upper()], '20', contract[5:-1]))
            for contract in dataframe.index
        ]
        dataframe = dataframe[['OPTIONS FTD']]
        dataframe.columns = ['EXPIRATION_DATE']
        dataframe['EXPIRATION_DATE'] = dataframe['EXPIRATION_DATE'].astype(np.datetime64)

        return dataframe
