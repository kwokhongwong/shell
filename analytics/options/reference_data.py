import datetime as dt
from analytics.constants import FUTURES_DELIVERY_MAP
from analytics.exceptions import BlackScholesCalculationError
from api import LocalClient as c
from functools import lru_cache


@lru_cache
def option_expiry(contract: str, exchange_code: str, month: str, year: str) -> dt.date:
    assert contract
    assert exchange_code
    assert month
    assert year

    symbol = f'CALENDAR_OPTION_{contract.upper()}'
    try:
        option_expiries = c.data(symbol=symbol)
    except FileNotFoundError:
        raise BlackScholesCalculationError(f'Missing option expiry market data for symbol {symbol}')

    contract_code = f'{FUTURES_DELIVERY_MAP[month.upper()]}{year}'

    return option_expiries.at[contract_code, 'EXPIRATION_DATE'].date()
