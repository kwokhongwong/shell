import datetime as dt
import os


# TODO initialise the trade/market dates each trading date
TRADE_DATE = dt.date(day=9, month=12, year=2022)
MARKET_DATE = dt.date(day=9, month=12, year=2022)
ROOT_PATH = os.path.sep.join(os.path.realpath(__file__).split(os.path.sep)[:-1])
MARKET_DATA_PATH = os.path.sep.join((ROOT_PATH, 'data'))
REST_API_URL = 'http://127.0.0.1:5000'


def env_variables() -> dict:
    return {
        'TRADE_DATE': TRADE_DATE,
        'MARKET_DATE': MARKET_DATE,
        'ROOT_PATH': ROOT_PATH,
        'MARKET_DATA_PATH': MARKET_DATA_PATH,
        'REST_API_URL': REST_API_URL
    }


def tweak_env(key: str, value: object) -> None:
    assert key

    if key.upper() in ('TRADE_DATE',):

        global TRADE_DATE

        try:
            import pandas as pd
            TRADE_DATE = pd.to_datetime(value).date()
        except:
            raise ValueError(f'Unsupported value {value} for TRADE_DATE tweak')
    else:
        raise ValueError(f'Unsupported env tweak for key {key}')
