import datetime as dt
import math
import pandas as pd
from analytics.constants import FUTURES_DELIVERY_MAP, CONTRACT_DEFAULT_EXCHANGE_MAP, CONTRACT_EXCHANGE_MAP
from api import LocalClient as c
from functools import lru_cache


@lru_cache
def implied_vol_model(
    trade_date: dt.date, contract: str, exchange_code: str, month: str, year: str
) -> float:
    assert trade_date
    assert contract
    assert exchange_code
    assert month
    assert year

    contract = contract.upper()
    exchange_code = (exchange_code or CONTRACT_DEFAULT_EXCHANGE_MAP[contract]).upper()
    expiration = f'{FUTURES_DELIVERY_MAP[month]}{year}'
    futures_code, options_code, __ = CONTRACT_EXCHANGE_MAP[(contract, exchange_code)]
    symbol = f'{contract}_{exchange_code}_{futures_code}_{options_code}_{expiration}_IVM'

    data = c.data(symbol=symbol)

    return data[data.index == pd.to_datetime(trade_date)]


@lru_cache
def ows_implied_vol(
        trade_date: dt.date, contract: str, exchange_code: str, strike: float, month: str, year: str
) -> float:
    assert trade_date
    assert contract
    assert exchange_code
    assert strike
    assert month
    assert year

    data_row = implied_vol_model(
        trade_date=trade_date, contract=contract, exchange_code=exchange_code, month=month, year=year
    )

    moneyness = math.log(strike / data_row['Future'][0])
    vol_implied = data_row['AtM'][0] \
                  + data_row['Beta1'][0] * moneyness \
                  + data_row['Beta2'][0] * moneyness ** 2 \
                  + data_row['Beta3'][0] * moneyness ** 3 \
                  + data_row['Beta4'][0] * moneyness ** 4 \
                  + data_row['Beta5'][0] * moneyness ** 5\
                  + data_row['Beta6'][0] * moneyness ** 6

    return float(vol_implied)


@lru_cache
def atm_strike(
        trade_date: dt.date, contract: str, exchange_code: str, month: str, year: str
) -> float:
    assert trade_date
    assert month
    assert year

    data_row = implied_vol_model(
        trade_date=trade_date, contract=contract, exchange_code=exchange_code, month=month, year=year
    )

    return float(data_row['Future'].values[0])


"""
# ----------
# Approximate Implied Volatility
#
# This function is used to choose a starting point for the
# search functions (Newton and bisection searches).
# Brenner & Subrahmanyam (1988), Feinstein (1988)
def approx_implied_vol(option_type, fs, x, t, r, b, cp):

    test_option_type(option_type)

    ebrt = math.exp((b - r) * t)
    ert = math.exp(-r * t)

    a = math.sqrt(2 * math.pi) / (fs * ebrt + x * ert)

    if option_type == "c":
        payoff = fs * ebrt - x * ert
    else:
        payoff = x * ert - fs * ebrt

    b = cp - payoff / 2
    c = (payoff ** 2) / math.pi

    v = (a * (b + math.sqrt(b ** 2 + c))) / math.sqrt(t)

    return v


# Find the Implied Volatility of an European (GBS) Option given a price
# using Newton-Raphson method for greater speed since Vega is available
def black_scholes_implied_vol(option_type, fs, x, t, r, b, cp, precision=.00001, max_steps=100):
    return _newton_implied_vol(gbs, option_type, x, fs, t, b, r, cp, precision, max_steps)


# Calculate Implied Volatility with a Newton Raphson search
def _newton_implied_vol(val_fn, option_type, x, fs, t, b, r, cp, precision=.00001, max_steps=100):
    # make sure a valid option type was entered
    test_option_type(option_type)

    # Estimate starting Vol, making sure it is allowable range
    v = approx_implied_vol(option_type, fs, x, t, r, b, cp)
    v = max(BlackScholesLimits.MIN_V, v)
    v = min(BlackScholesLimits.MAX_V, v)

    # Calculate the value at the estimated vol
    value, delta, gamma, theta, vega, rho = val_fn(option_type, fs, x, t, r, b, v)
    min_diff = abs(cp - value)

    # Newton-Raphson Search
    countr = 0
    while precision <= abs(cp - value) <= min_diff and countr < max_steps:

        v = v - (value - cp) / vega
        if (v > BlackScholesLimits.MAX_V) or (v < BlackScholesLimits.MIN_V):
            break

        value, delta, gamma, theta, vega, rho = val_fn(option_type, fs, x, t, r, b, v)
        min_diff = min(abs(cp - value), min_diff)

        # keep track of how many loops
        countr += 1

    # check if function converged and return a value
    if abs(cp - value) < precision:
        # the search function converged
        return v
    else:
        # if the search function didn't converge, try a bisection search
        return _bisection_implied_vol(val_fn, option_type, fs, x, t, r, b, cp, precision, max_steps)


# ----------
# Find the Implied Volatility using a Bisection search
def _bisection_implied_vol(val_fn, option_type, fs, x, t, r, b, cp, precision=.00001, max_steps=100):

    # Estimate Upper and Lower bounds on volatility
    # Assume American Implied vol is within +/- 50% of the GBS Implied Vol
    v_mid = approx_implied_vol(option_type, fs, x, t, r, b, cp)

    if (v_mid <= BlackScholesLimits.MIN_V) or (v_mid >= BlackScholesLimits.MAX_V):
        # if the volatility estimate is out of bounds, search entire allowed vol space
        v_low = BlackScholesLimits.MIN_V
        v_high = BlackScholesLimits.MAX_V
        v_mid = (v_low + v_high) / 2
    else:
        # reduce the size of the vol space
        v_low = max(BlackScholesLimits.MIN_V, v_mid * .5)
        v_high = min(BlackScholesLimits.MAX_V, v_mid * 1.5)

    # Estimate the high/low bounds on price
    cp_mid = val_fn(option_type, fs, x, t, r, b, v_mid)[0]

    # initialize bisection loop
    current_step = 0
    diff = abs(cp - cp_mid)

    # Keep bisection volatility until correct price is found
    while (diff > precision) and (current_step < max_steps):
        current_step += 1

        # Cut the search area in half
        if cp_mid < cp:
            v_low = v_mid
        else:
            v_high = v_mid

        cp_low = val_fn(option_type, fs, x, t, r, b, v_low)[0]
        cp_high = val_fn(option_type, fs, x, t, r, b, v_high)[0]

        v_mid = v_low + (cp - cp_low) * (v_high - v_low) / (cp_high - cp_low)
        v_mid = max(BlackScholesLimits.MIN_V, v_mid)  # enforce high/low bounds
        v_mid = min(BlackScholesLimits.MAX_V, v_mid)  # enforce high/low bounds

        cp_mid = val_fn(option_type, fs, x, t, r, b, v_mid)[0]
        diff = abs(cp - cp_mid)

    # return output
    if abs(cp - cp_mid) < precision:
        return v_mid
    else:
        raise BlackScholesCalculationError(
            "Implied Vol did not converge. Best Guess={0}, Price diff={1}, Required Precision={2}".format(v_mid, diff,
                                                                                                          precision))
"""
