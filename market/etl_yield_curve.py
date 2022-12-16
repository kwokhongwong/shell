import numpy as np
import pandas as pd
from market.etl_adapter import BaseETLAdapter


class FEDUSTAdapter(BaseETLAdapter):

    def transform(self, url: str, params: dict) -> pd.DataFrame:
        assert url

        dataframe = pd.read_csv(
            url,
            skiprows=5,
            index_col='Time Period',
        )
        dataframe.replace('ND', np.nan, regex=True, inplace=True)
        dataframe.dropna(how='all', inplace=True)
        dataframe.index = pd.to_datetime(dataframe.index)
        for column in dataframe.columns:
            dataframe[column] = dataframe[column].astype(np.float32)

        # effective_annual_rate & year fractions
        effective_annual_rates = pd.DataFrame(
            data=np.log((1 + dataframe.values / 200) ** 2),
            index=dataframe.index,
            columns=dataframe.columns
        )

        return effective_annual_rates
