import datetime as dt
import pytest

from analytics.curves.yield_curve import interpolate_rate
from analytics.exceptions import BlackScholesCalculationError


def test_interpolate_rate():
    rate = interpolate_rate(
        trade_date=dt.date(day=5, month=12, year=2022), expiry_date=dt.date(day=5, month=12, year=2025)
    )

    assert rate > 0

    with pytest.raises(BlackScholesCalculationError):
        interpolate_rate(
            trade_date=dt.date(day=5, month=12, year=2022), expiry_date=dt.date(day=5, month=12, year=2100)
        )
