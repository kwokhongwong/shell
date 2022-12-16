import datetime as dt
from analytics.options.volatility import implied_vol_model, ows_implied_vol, atm_strike


def test_implied_vol_model():
    trade_date = dt.date(day=5, month=12, year=2022)
    dataframe = implied_vol_model(
        trade_date=trade_date, contract='BRENT', exchange_code='ICE', month='JAN', year=2025
    )

    assert len(dataframe) > 0
    assert dataframe.columns.tolist() == [
        'Future', 'AtM', 'RR25', 'RR10', 'Fly25', 'Fly10', 'Beta1', 'Beta2', 'Beta3', 'Beta4', 'Beta5', 'Beta6',
        'MinMoney', 'MaxMoney', 'DtE', 'DtT']


def test_ows_implied_vol():
    trade_date = dt.date(day=5, month=12, year=2022)
    implied_vol = ows_implied_vol(
        trade_date=trade_date, contract='BRENT', exchange_code='ICE', strike=70.5, month='JAN', year=2025
    )

    assert implied_vol > 0


def test_atm_strike():
    trade_date = dt.date(day=5, month=12, year=2022)
    _atm_strike = atm_strike(
        trade_date=trade_date, contract='BRENT', exchange_code='ICE', month='JAN', year=2025
    )

    assert _atm_strike > 0
