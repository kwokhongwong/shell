import env
import math
from scipy.stats import norm
from analytics.constants import BlackScholesLimits
from analytics.exceptions import BlackScholesInputError
from functools import lru_cache


class BlackScholesOptionPricer:

    __slots__ = ('option_type', 'x', 'fs', 't', 'b', 'r', 'v', 'd1', 'd2')

    def __init__(
            self, option_type: str, x: float, fs: float, t: float, b: float, r: float, v: float
    ):
        assert option_type
        assert x
        assert fs
        assert t
        assert r
        assert v

        self.option_type = option_type
        self.x = x
        self.fs = fs
        self.t = t
        self.b = b
        self.r = r
        self.v = v

        self.validate_inputs(
            option_type=self.option_type, x=self.x, fs=self.fs, t=self.t, b=self.b, r=self.r, v=self.v
        )

        t_sqrt = math.sqrt(self.t)
        self.d1 = (math.log(self.fs / self.x) + (self.b + (self.v * self.v) / 2) * self.t) / (self.v * t_sqrt)
        self.d2 = self.d1 - self.v * t_sqrt

    @staticmethod
    def validate_inputs(option_type: str, x: float, fs: float, t: float, b: float, r: float, v: float) -> None:
        assert option_type
        assert x
        assert fs
        assert t
        assert r

        if option_type.lower() not in ("c", "p"):
            raise BlackScholesInputError(f"Invalid Input option_type ({option_type}). Acceptable value are: c, p")

        if (x < BlackScholesLimits.MIN_X) or (x > BlackScholesLimits.MAX_X):
            raise BlackScholesInputError(
                f"Invalid Input Strike Price {x}. "
                f"Acceptable range for inputs is {BlackScholesLimits.MIN_X} to {BlackScholesLimits.MAX_X}")

        if (fs < BlackScholesLimits.MIN_FS) or (fs > BlackScholesLimits.MAX_FS):
            raise BlackScholesInputError(
                f"Invalid Input Underlier Price (FS). "
                f"Acceptable range for inputs is {BlackScholesLimits.MIN_FS} to {BlackScholesLimits.MAX_FS}")

        if (t < BlackScholesLimits.MIN_T) or (t > BlackScholesLimits.MAX_T):
            raise BlackScholesInputError(
                f"Invalid Input Time (T = {t}). "
                f"Acceptable range for inputs is {BlackScholesLimits.MIN_T} to {BlackScholesLimits.MAX_T}")

        if (b < BlackScholesLimits.MIN_b) or (b > BlackScholesLimits.MAX_b):
            raise BlackScholesInputError(
                f"Invalid Input Cost of Carry (carry_cost = {b}). "
                f"Acceptable range for inputs is {BlackScholesLimits.MIN_b} to {BlackScholesLimits.MAX_b}")

        if (r < BlackScholesLimits.MIN_r) or (r > BlackScholesLimits.MAX_r):
            raise BlackScholesInputError(
                f"Invalid Input Risk Free Rate (rate = {r}). "
                f"Acceptable range for inputs is {BlackScholesLimits.MIN_r} to {BlackScholesLimits.MAX_r}")

        if (v < BlackScholesLimits.MIN_V) or (v > BlackScholesLimits.MAX_V):
            raise BlackScholesInputError(
                f"Invalid Input Implied Volatility (volatility = {v}). "
                f"Acceptable range for inputs is {BlackScholesLimits.MIN_V} to {BlackScholesLimits.MAX_V}")

    def pv(self) -> float:

        if self.option_type.lower() == 'c':
            pv = self.fs * math.exp((self.b - self.r) * self.t) * norm.cdf(self.d1)\
                 - self.x * math.exp(-self.r * self.t) * norm.cdf(self.d2)
        elif self.option_type.lower() == 'p':
            pv = self.x * math.exp(-self.r * self.t) * norm.cdf(-self.d2) \
                 - (self.fs * math.exp((self.b - self.r) * self.t) * norm.cdf(-self.d1))

        return pv

    @lru_cache
    def greeks(self) -> dict:

        b = self.b
        r = self.r
        t = self.t
        d1 = self.d1
        fs = self.fs
        v = self.v
        t_sqrt = math.sqrt(self.t)
        x = self.x
        d2 = self.d2

        if self.option_type.lower() == "c":
            delta = math.exp((b - r) * t) * norm.cdf(d1)
            gamma = math.exp((b - r) * t) * norm.pdf(d1) / (fs * v * t_sqrt)
            theta = -(fs * v * math.exp((b - r) * t) * norm.pdf(d1)) / (2 * t_sqrt) \
                    - (b - r) * fs * math.exp((b - r) * t) * norm.cdf(d1) - r * x * math.exp(-r * t) * norm.cdf(d2)
            vega = math.exp((b - r) * t) * fs * t_sqrt * norm.pdf(d1)
            rho = x * t * math.exp(-r * t) * norm.cdf(d2)
        else:
            delta = -math.exp((b - r) * t) * norm.cdf(-d1)
            gamma = math.exp((b - r) * t) * norm.pdf(d1) / (fs * v * t_sqrt)
            theta = -(fs * v * math.exp((b - r) * t) * norm.pdf(d1)) / (2 * t_sqrt) + (b - r) * fs * math.exp(
                (b - r) * t) * norm.cdf(-d1) + r * x * math.exp(-r * t) * norm.cdf(-d2)
            vega = math.exp((b - r) * t) * fs * t_sqrt * norm.pdf(d1)
            rho = -x * t * math.exp(-r * t) * norm.cdf(-d2)

        return {
            'DELTA': delta,
            'GAMMA': gamma,
            'THETA': theta,
            'VEGA': vega,
            'RHO': rho
        }


class Black76CommodityOptionPricer(BlackScholesOptionPricer):

    __slots__ = ('contract', 'exchange_code', 'month', 'year', 'expiry_date')

    def __init__(
            self, option_type: str, contract: str, exchange_code: str, month: str, year: str, strike = None
    ):
        assert contract
        assert exchange_code
        assert month
        assert year

        from analytics.options.reference_data import option_expiry

        self.contract = contract
        self.exchange_code = exchange_code
        self.month = month
        self.year = year
        self.expiry_date = option_expiry(
            contract=self.contract,
            exchange_code=self.exchange_code,
            month=self.month,
            year=self.year
        )

        x_atm = self.atm_strike()
        x = strike or x_atm
        t = (self.expiry_date - env.TRADE_DATE).days / 365.25
        b = 0
        fs = x_atm
        r = self.rate()
        v = self.implied_vol(strike=x)

        super(Black76CommodityOptionPricer, self).__init__(
            option_type=option_type, x=x, fs=fs, t=t, b=b, r=r, v=v
        )

    @lru_cache
    def atm_strike(self) -> float:
        from analytics.options.volatility import atm_strike

        return atm_strike(
            trade_date=env.TRADE_DATE,
            contract=self.contract,
            exchange_code=self.exchange_code,
            month=self.month,
            year=self.year
        )

    @lru_cache
    def implied_vol(self, strike: float) -> float:
        assert strike

        from analytics.options.volatility import ows_implied_vol

        return ows_implied_vol(
            trade_date=env.TRADE_DATE,
            contract=self.contract,
            exchange_code=self.exchange_code,
            strike=strike,
            month=self.month,
            year=self.year
        )

    @lru_cache
    def rate(self) -> float:
        from analytics.curves.yield_curve import interpolate_rate

        return interpolate_rate(
            trade_date=env.TRADE_DATE,
            expiry_date=self.expiry_date
        )

    def lot_factor(self):
        from analytics.constants import CONTRACT_EXCHANGE_MAP

        __, __, lot_size = CONTRACT_EXCHANGE_MAP[(self.contract, self.exchange_code)]

        return lot_size
