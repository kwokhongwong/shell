"""

https://docs.data.nasdaq.com/docs/in-depth-usage

GET https://data.nasdaq.com/api/v3/datasets/{database_code}/{dataset_code}/data.{return_format}

database-code : OWF

Implied Volatility Model time-series:
OWF/{exchange code}_{futures code}_{options code}_{expiration}_IVM

Implied Volatility Surface time-series:
OWF/{exchange code}_{futures code}_{options code}_{expiration}_IVS

exchange code:
CBT, CME, CMX, ENX, ICE, NYM, NYX

futures code:
S for soybeans, CL for crude oil

options code:
EC for monthly euro fx, 1X for weekly euro fx

expiration (options contract expiration):
F2015 for January 2015
1W, 1M, 2M, 3M, 6M, 9M, and 1Y for the IVM time-series
1W, 1M, 2M, 3M, 6M, 9M, 1Y, 2Y and 5Y for the IVS time-series

https://data.nasdaq.com/data/OWF-optionworks-futures-options/documentation

CONTRACT        EXCHANGE CODE   FUTURES CODE    OPTIONS CODE
Brent Crude Oil ICE             B               B
WTI Crude Oil   NYM             CL              CL
WTI Crude Oil   ICE             T               T

e.g. NYM WTI Crude Oil CL N2019 Futures Options Implied Volatility Surface
OWF/{exchange code}_{futures code}_{options code}_{expiration}_IVS
OWF/NYM_CL_CL_N2019_IVS

Expiration codes:
January	F
February	G
March	H
April	J
May	K
June	M
July	N
August	Q
September	U
October	V
November	X
December	Z

The OWF data feed provides a smooth volatility skew curve using this 6-degree polynomial model:
IV = AtM + Beta1*x + Beta2*x^2 + Beta3*x^3 + Beta4*x^4 + Beta5*x^5 + Beta6*x^6

IV = implied volatility at a given strike price
AtM = at-the-money implied volatility
x = "moneyness" of the strike = ln (strike price / futures price)
Beta1 to Beta6 = model coefficients

=> Use IVM download & 6 degree polynomial skew curve model
"""

import numpy as np
import pandas as pd
from analytics.constants import FUTURES_DELIVERY_MAP
from market.etl_adapter import BaseETLAdapter


api_key = 'uM-pW7KJQ61e_H7i6TEB'
database_code = 'OWF'


class QuandlOWFImpliedVolsAdapter(BaseETLAdapter):

    def transform(self, url, params: dict) -> pd.DataFrame:
        assert url
        assert params

        options_code = params['OPTIONS_CODE']
        exchange_code = params['EXCHANGE_CODE']
        futures_code = params['FUTURES_CODE']
        month = params['MONTH']
        year = params['YEAR']

        expiration = f'{FUTURES_DELIVERY_MAP[month]}{year}'
        dataset_code = f'{exchange_code}_{futures_code}_{options_code}_{expiration}_IVM'
        url = f'{url}/{dataset_code}.csv?api_key={api_key}'

        dataframe = pd.read_csv(
            url,
            index_col='Date',
            dtype={
                'Future': np.float32,
                'AtM': np.float32,
                'RR25': np.float32,
                'RR10': np.float32,
                'Fly25': np.float32,
                'Fly10': np.float32,
                'Beta1': np.float32,
                'Beta2': np.float32,
                'Beta3': np.float32,
                'Beta4': np.float32,
                'Beta5': np.float32,
                'Beta6': np.float32,
                'MinMoney': np.float32,
                'MaxMoney': np.float32,
                'DtE': np.float32,
                'DtT': np.float32
            }
        )

        dataframe.index = pd.to_datetime(dataframe.index)

        return dataframe
