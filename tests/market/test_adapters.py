import os

from api import LocalClient as c
from env import ROOT_PATH


def test_ice_option_expiries_adapter():
    from market.etl_option_expiries import ICEOptionExpiriesAdapter

    symbol = 'CALENDAR_OPTION_BRENT'
    url = os.path.sep.join((ROOT_PATH, 'notebooks', 'ProductSpecExpiryDates_BRENT_OPTIONS.csv'))
    dataframe = ICEOptionExpiriesAdapter(
        symbol=symbol,
        url=url,
        use_local_client=True
    ).run(save=True)

    assert dataframe.columns.tolist() == ['EXPIRATION_DATE']
    assert len(dataframe) > 0
    assert dataframe.equals(c.data(symbol=symbol))


def test_cme_option_expiries_adapter():
    from market.etl_option_expiries import CMEOptionExpiriesAdapter

    symbol = 'CALENDAR_OPTION_HH'
    url = os.path.sep.join((ROOT_PATH, 'notebooks', 'product-calendar_HH_OPTIONS.xls'))
    dataframe = CMEOptionExpiriesAdapter(
        symbol=symbol,
        url=url,
        use_local_client=True
    ).run(save=True)

    assert dataframe.columns.tolist() == ['EXPIRATION_DATE']
    assert len(dataframe) > 0
    assert dataframe.equals(c.data(symbol=symbol))


def test_fed_ust_adapter():
    from market.etl_yield_curve import FEDUSTAdapter

    symbol = 'RIFLGFC'
    url = os.path.sep.join((ROOT_PATH, 'notebooks', 'FRB_H15.csv'))
    dataframe = FEDUSTAdapter(
        symbol=symbol,
        url=url,
        use_local_client=True
    ).run(save=True)

    assert dataframe.columns.tolist() == [
        'RIFLGFCM01_N.B', 'RIFLGFCM03_N.B', 'RIFLGFCM06_N.B', 'RIFLGFCY01_N.B', 'RIFLGFCY02_N.B', 'RIFLGFCY03_N.B',
        'RIFLGFCY05_N.B', 'RIFLGFCY07_N.B', 'RIFLGFCY10_N.B', 'RIFLGFCY20_N.B', 'RIFLGFCY30_N.B'
    ]
    assert len(dataframe) > 0
    assert dataframe.equals(c.data(symbol=symbol))


def test_quandl_owf_implied_vols_adapter():
    from analytics.constants import FUTURES_DELIVERY_MAP
    from market.etl_implied_vols import QuandlOWFImpliedVolsAdapter

    url = f'https://data.nasdaq.com/api/v3/datasets/OWF'
    contract = 'BRENT'
    exchange_code = 'ICE'
    futures_code = 'B'
    options_code = 'B'
    year = '2025'
    month = 'JAN'
    params = {
        'EXCHANGE_CODE': exchange_code,
        'FUTURES_CODE': futures_code,
        'OPTIONS_CODE': options_code,
        'YEAR': year,
        'MONTH': month
    }
    expiration = f'{FUTURES_DELIVERY_MAP[month]}{year}'
    symbol = f'{contract}_{exchange_code}_{futures_code}_{options_code}_{expiration}_IVM'

    dataframe = QuandlOWFImpliedVolsAdapter(
        symbol=symbol,
        url=url,
        use_local_client=True,
        params=params
    ).run(save=True)

    assert dataframe.columns.tolist() == [
        'Future', 'AtM', 'RR25', 'RR10', 'Fly25', 'Fly10', 'Beta1', 'Beta2', 'Beta3', 'Beta4', 'Beta5', 'Beta6',
        'MinMoney', 'MaxMoney', 'DtE', 'DtT'
    ]
    assert len(dataframe) > 0
    assert dataframe.equals(c.data(symbol=symbol))
