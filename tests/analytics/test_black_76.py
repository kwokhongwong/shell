import pytest
from analytics.exceptions import BlackScholesCalculationError
from analytics.options.black_scholes import Black76CommodityOptionPricer, BlackScholesOptionPricer


def test_commodity_option_brent():
    pricer_call = Black76CommodityOptionPricer(
        contract='BRENT', exchange_code='ICE', month='JAN', year='2025', option_type='C'
    )
    pv_call = pricer_call.pv()
    assert isinstance(pv_call, float)

    pricer_put = Black76CommodityOptionPricer(
        contract='BRENT', exchange_code='ICE', month='JAN', year='2025', option_type='P'
    )
    pv_put = pricer_put.pv()
    assert isinstance(pv_put, float)

    with pytest.raises(BlackScholesCalculationError):
        Black76CommodityOptionPricer(
            contract='XXX', exchange_code='ICE', month='JAN', year='2025', option_type='C'
        )


def test_option_benchmark_price():
    """
    pv = black_76('c', fs=19, x=19, t=0.75, r=0.10, v=0.28)
    1.70105072524
    """
    pricer = BlackScholesOptionPricer(
        option_type='C', x=19, fs=19, t=0.75, b=0, r=0.1, v=0.28
    )
    pv = pricer.pv()

    assert round(pv, 9) == round(1.70105072524, 9)
