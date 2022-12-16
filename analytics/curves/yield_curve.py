import datetime
import pandas as pd
from analytics.exceptions import BlackScholesCalculationError
from api import LocalClient as c
from functools import lru_cache


@lru_cache
def interpolate_rate(
        trade_date: datetime.date, expiry_date: datetime.date
) -> float:
    assert trade_date
    assert expiry_date
    assert expiry_date > trade_date

    # Fed Reserve US Treasury Constant Maturity
    symbol = 'RIFLGFC'
    dataframe = c.data(symbol=symbol)
    dataframe.columns = [1/12, 3/12, 6/12, 1, 2, 3, 5, 7, 10, 20, 30]
    data_row = dataframe.loc[pd.Timestamp(trade_date)]
    year_faction = (expiry_date - trade_date).days / 365.25

    if year_faction < data_row.index[0] or year_faction > data_row.index[-1]:
        raise BlackScholesCalculationError(f'Expiry date {expiry_date} is not supported on the yield curve')

    index = None
    for i, index_value in enumerate(data_row.index):
        if index_value >= year_faction:
            index = data_row.index[i - 1:]
            break
    interpolation_rates = data_row[index]

    """
    Example: 6.3Y rate -> use 5Y (1.49%) & 7Y (2.13%) interpolation
    effective_annual_rate_5y = math.log(1 + (1+0.0149/2)**(2) - 1) = 0.01484477163127614
    effective_annual_rate_7y = math.log(1 + (1+0.0213/2)**(2) - 1) = 0.02118737642173995
    weight_5y = (7 - 6.3)/(7 - 5)
    weight_7y = 1 - weight_5y
    rate_interpolated = weight_5y * effective_annual_rate_5y + weight_7y * effective_annual_rate_7y
    """
    weight_1 = (index[1] - year_faction) / (index[1] - index[0])
    weight_2 = 1 - weight_1
    rate = weight_1 * interpolation_rates.values[0] + weight_2 * interpolation_rates.values[1]

    return rate
