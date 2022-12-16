import env
import json
import os
import pandas as pd
import requests
from abc import ABC, abstractmethod
from market.datastore_adapter import DataAPI


class BaseClient(ABC):

    @classmethod
    def endpoints(cls):
        """
        :return: Sequence of available public API endpoints
        """
        return [method_name for method_name in dir(cls) if not method_name.startswith('_')]

    @staticmethod
    @abstractmethod
    def env_variables() -> dict:
        pass

    @staticmethod
    @abstractmethod
    def tweak_env(
            key: str, value: object
    ) -> None:
        pass

    @staticmethod
    @abstractmethod
    def option_price(
            option_type: str, x: float, fs: float, t: float, b: float, r: float, v: float
    ) -> float:
        pass

    @staticmethod
    @abstractmethod
    def option_greeks(
            option_type: str, x: float, fs: float, t: float, b: float, r: float, v: float
    ) -> float:
        pass

    @staticmethod
    @abstractmethod
    def commodity_option_price(
            contract: str, month: str, year: str, option_type: str,
            strike: str = None, exchange_code: str = None, lot_price: bool = False
    ) -> float:
        pass

    @staticmethod
    @abstractmethod
    def commodity_option_greeks(
            contract: str, exchange_code: str, month: str, year: str, option_type: str, strike: str
    ) -> float:
        pass

    @staticmethod
    @abstractmethod
    def data(symbol: str) -> object:
        pass

    @staticmethod
    @abstractmethod
    def symbols() -> list:
        pass

    @staticmethod
    @abstractmethod
    def save(symbol: str, dataframe: pd.DataFrame) -> str:
        pass


class LocalClient(BaseClient):

    @staticmethod
    def env_variables() -> dict:
        return env.env_variables()

    @staticmethod
    def tweak_env(
            key: str, value: object
    ) -> None:
        assert key

        from env import tweak_env

        tweak_env(key=key, value=value)

    @staticmethod
    def option_price(
            option_type: str, x: float, fs: float, t: float, b: float, r: float, v: float
    ) -> float:
        assert option_type
        assert x
        assert fs
        assert t
        assert b is not None
        assert r
        assert v

        from analytics.options.black_scholes import BlackScholesOptionPricer

        pricer = BlackScholesOptionPricer(
            option_type=option_type, x=x, fs=fs, t=t, b=b, r=r, v=v
        )

        return pricer.pv()

    @staticmethod
    def option_greeks(
            option_type: str, x: float, fs: float, t: float, b: float, r: float, v: float
    ) -> float:
        assert option_type
        assert x
        assert fs
        assert t
        assert b is not None
        assert r
        assert v

        from analytics.options.black_scholes import BlackScholesOptionPricer

        pricer = BlackScholesOptionPricer(
            option_type=option_type, x=x, fs=fs, t=t, b=b, r=r, v=v
        )

        return pricer.greeks()

    @staticmethod
    def commodity_option_price(
            contract: str, month: str, year: str, option_type: str,
            strike: str = None, exchange_code: str = None, lot_price: bool = False
    ) -> float:
        assert contract
        assert exchange_code
        assert month
        assert year
        assert option_type

        from analytics.options.black_scholes import Black76CommodityOptionPricer

        pricer = Black76CommodityOptionPricer(
            contract=contract,
            exchange_code=exchange_code,
            month=month,
            year=year,
            option_type=option_type,
            strike=strike
        )
        lot_factor = pricer.lot_factor() if lot_price else 1.

        return pricer.pv() * lot_factor

    @staticmethod
    def commodity_option_greeks(
            contract: str, exchange_code: str, month: str, year: str, option_type: str, strike: str
    ) -> float:
        assert contract
        assert exchange_code
        assert month
        assert year
        assert option_type

        from analytics.options.black_scholes import Black76CommodityOptionPricer

        pricer = Black76CommodityOptionPricer(
            contract=contract,
            exchange_code=exchange_code,
            month=month,
            year=year,
            option_type=option_type,
            strike=strike
        )

        return pricer.greeks()

    @staticmethod
    def data(symbol: str) -> object:
        assert symbol

        return DataAPI.query(symbol=symbol)

    @staticmethod
    def symbols() -> list:

        import glob

        return [
            file_path.split(os.path.sep)[-1].split('.')[0]
            for file_path in glob.glob(os.path.sep.join((env.MARKET_DATA_PATH, '*.*')))
            if file_path.endswith('.parquet')
        ]

    @staticmethod
    def save(symbol: str, dataframe: pd.DataFrame) -> str:
        assert symbol
        assert dataframe is not None

        return DataAPI.persist(symbol=symbol, dataframe=dataframe)


class RestClient(BaseClient):

    """
    Proxy Client API for REST API
    """

    @staticmethod
    def env_variables() -> dict:
        """
        :return: dict of system wide environment variables
        """

        url = f'{env.REST_API_URL}/env_variables'
        response = requests.get(url)

        return json.loads(response.content)['ENV_VARIABLES']

    @staticmethod
    def tweak_env(
            key: str, value: object
    ) -> None:
        """
        Endpoint to allow tweaking of system environment variables, use env_variables() to view available keys

        :param key: str key for env variable to tweak
        :param value: new value to tweak the env variable to
        :return: Success or error message
        """
        assert key
        assert value

        url = f'{env.REST_API_URL}/tweak_env?KEY={key}&VALUE={value}'

        return requests.get(url).text

    @staticmethod
    def option_price(
            option_type: str, x: float, fs: float, t: float, b: float, r: float, v: float
    ) -> float:
        """
        Generalised Black Scholes 73 option pricer endpoint

        :param option_type: Use either 'c' (call) or 'p' (put)
        :param x: Option strike price
        :param fs: Price of underlying
        :param t: Time to expiry
        :param b: Cost of carry / yield dividend etc
        :param r: Risk free rate
        :param v: Volatility
        :return: Option price/premium
        """
        assert option_type
        assert x
        assert fs
        assert t
        assert b is not None
        assert r
        assert v

        url = f'{env.REST_API_URL}/option_price' \
              f'?OPTION_TYPE={option_type}&X={x}&FS={fs}&T={t}&B={b}&R={r}&V={v}'

        result = requests.get(url).text

        try:
            return float(result)
        except ValueError:
            return result

    @staticmethod
    def option_greeks(
            option_type: str, x: float, fs: float, t: float, b: float, r: float, v: float
    ) -> float:
        """
        Generalised Black Scholes 73 option greeks endpoint

        :param option_type: Use either 'c' (call) or 'p' (put)
        :param x: Option strike price
        :param fs: Price of underlying
        :param t: Time to expiry
        :param b: Cost of carry / yield dividend etc
        :param r: Risk free rate
        :param v: Volatility
        :return: dict of Option greeks (Delta, Gamma, Theta, Vega, Rho)
        """
        assert option_type
        assert x
        assert fs
        assert t
        assert b is not None
        assert r
        assert v

        import ast

        url = f'{env.REST_API_URL}/option_greeks' \
              f'?OPTION_TYPE={option_type}&X={x}&FS={fs}&T={t}&B={b}&R={r}&V={v}'

        result = requests.get(url).content

        try:
            return ast.literal_eval(result.decode('UTF-8'))
        except ValueError:
            return result

    @staticmethod
    def commodity_option_price(
            contract: str, month: str, year: str, option_type: str,
            strike: str = None, exchange_code: str = None, lot_price: bool = False
    ) -> float:
        """
        Black 76 option pricer endpoint

        Implied volatility is calculated using the OptionWorks Futures Implied Volatility Model (IVM):
        - This assumes a volatility skew curve using a 6-degree polynomial model
        - IV = AtM + Beta1*x + Beta2*x^2 + Beta3*x^3 + Beta4*x^4 + Beta5*x^5 + Beta6*x^6 (where x is moneyness)
        - https://data.nasdaq.com/data/OWF-optionworks-futures-options/documentation

        Time to expiry is calculated using market data option calenders for the specific Option contract code

        Cost of carry is set to zero

        Risk free rate is weighted interpolation using Fed Reserver daily Treasury Contant Maturity Rates
        - https://support.carta.com/s/article/black-scholes

        :param contract: Options contract e.g. 'BRENT', 'WTI', 'HH' etc
        :param month: Expiry month e.g. 'JAN', 'FEB', 'MAR', etc
        :param year: Expiry year e.g. '2025'
        :param option_type: Use either 'c' (call) or 'p' (put)
        :param strike: Optional, defaults to ATM if not set
        :param exchange_code: Optional, e.g. 'ICE', 'NYM' etc
        :param lot_price: Optional, set to true to return the Option price * Futures lot size
        :return: Commodity option price/premium
        """
        assert contract
        assert month
        assert year
        assert option_type

        url = f'{env.REST_API_URL}/commodity_option_price' \
              f'?CONTRACT={contract}&MONTH={month}&YEAR={year}&OPTION_TYPE={option_type}&LOT_PRICE={lot_price}'
        if strike:
            url = url + f'&STRIKE={strike}'
        if exchange_code:
            url = url + f'&EXCHANGE_CODE={exchange_code}'

        result = requests.get(url).text

        try:
            return float(result)
        except ValueError:
            return result

    @staticmethod
    def commodity_option_greeks(
            contract: str, month: str, year: str, option_type: str, strike: str = None, exchange_code: str = None
    ) -> float:
        """
        Commodity option greeks, see endpoint commodity_option_price() for model implementation details

        :param contract: Options contract e.g. 'BRENT', 'WTI', 'HH' etc
        :param month: Expiry month e.g. 'JAN', 'FEB', 'MAR', etc
        :param year: Expiry year e.g. '2025'
        :param option_type: Use either 'c' (call) or 'p' (put)
        :param strike: Optional, defaults to ATM if not set
        :param exchange_code: Optional, e.g. 'ICE', 'NYM' etc
        :return: dict of Commodity option greeks (Delta, Gamma, Theta, Vega, Rho)
        """
        assert contract
        assert month
        assert year
        assert option_type

        import ast

        url = f'{env.REST_API_URL}/commodity_option_greeks' \
              f'?CONTRACT={contract}&MONTH={month}&YEAR={year}&OPTION_TYPE={option_type}'
        if strike:
            url = url + f'&STRIKE={strike}'
        if exchange_code:
            url = url + f'&EXCHANGE_CODE={exchange_code}'

        result = requests.get(url).content

        try:
            return ast.literal_eval(result.decode('UTF-8'))
        except ValueError:
            return result

    @staticmethod
    def data(symbol: str) -> object:
        """
        Data query endpoint

        :param symbol: Data symbol, see symbols() endpoint for existing data symbols
        :return: Table (pandas) data, TODO scalers
        """
        assert symbol

        import io
        import pyarrow.parquet as pq

        url = f'{env.REST_API_URL}/data?SYMBOL={symbol}'

        response = requests.get(url)
        table = pq.read_table(io.BytesIO(response.content))
        return table.to_pandas()

    @staticmethod
    def symbols() -> list:
        """
        :return: list of existing data symbols
        """

        url = f'{env.REST_API_URL}/symbols'
        response = requests.get(url)

        return json.loads(response.content)['SYMBOLS']

    @staticmethod
    def save(symbol: str, dataframe: pd.DataFrame) -> str:
        """
        Data upload endpoint, supports table (pandas) data

        TODO scalers etc

        :param symbol: str symbol
        :param dataframe: pandas Dataframe
        :return: str message indicating save state
        """
        assert symbol
        assert dataframe is not None

        import tempfile

        file_path_local = os.path.sep.join((tempfile.gettempdir(), f'{symbol}.parquet'))
        dataframe.to_parquet(file_path_local)

        url = f'{env.REST_API_URL}/save'
        params = {
            'SYMBOL': symbol,
            'FILE_EXTENSION': '.parquet'
        }
        files = {"file": open(file_path_local, 'rb')}

        return requests.post(url, params=params, files=files).text


print(f'***** Shell Trading API *****')
for key, value in env.env_variables().items():
    print(f'{key} = {value}')
