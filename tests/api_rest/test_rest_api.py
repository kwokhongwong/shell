import json
import pytest
from app import app as flask_app
from env import ROOT_PATH


@pytest.fixture
def app():
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


def test_save(app, client):
    import os
    import tempfile
    from market.etl_option_expiries import ICEOptionExpiriesAdapter

    symbol = 'CALENDAR_OPTION_BRENT'
    url = os.path.sep.join((ROOT_PATH, 'notebooks', 'ProductSpecExpiryDates_BRENT_OPTIONS.csv'))
    dataframe = ICEOptionExpiriesAdapter(
        symbol=symbol,
        url=url,
        use_local_client=True
    ).run(save=False)

    file_name = f'{symbol}.parquet'
    file_path_local = os.path.sep.join((tempfile.gettempdir(), file_name))
    dataframe.to_parquet(file_path_local)
    file = open(file_path_local, 'rb')
    data = {
        'file': file
    }

    response = client.post(f'/save?SYMBOL={symbol}&FILE_EXTENSION=.parquet', data=data)

    assert response.status_code == 200
    assert response.data.decode('UTF-8') == f'Market data save successful for symbol {symbol}'


def test_symbols(app, client):
    response = client.get('/symbols')
    symbols = json.loads(response.data)['SYMBOLS']

    assert response.status_code == 200
    assert len(symbols) > 0


def test_commodity_option_price(app, client):
    option_type = 'C'
    contract = 'BRENT'
    year = '2025'
    month = 'JAN'
    url = f'/commodity_option_price?CONTRACT={contract}&MONTH={month}&YEAR={year}&OPTION_TYPE={option_type}'

    response = client.get(url)

    assert response.status_code == 200
    assert float(response.data.decode('UTF-8')) > 0.


def test_commodity_option_greeks(app, client):
    import ast

    option_type = 'P'
    contract = 'BRENT'
    year = '2025'
    month = 'FEB'
    url = f'/commodity_option_greeks?CONTRACT={contract}&MONTH={month}&YEAR={year}&OPTION_TYPE={option_type}'

    response = client.get(url)

    assert response.status_code == 200

    greeks = ast.literal_eval(response.data.decode('UTF-8'))
    assert isinstance(greeks['DELTA'], float)
    assert isinstance(greeks['GAMMA'], float)
    assert isinstance(greeks['THETA'], float)
    assert isinstance(greeks['VEGA'], float)
    assert isinstance(greeks['RHO'], float)


def test_data(app, client):
    import io
    import pyarrow.parquet as pq

    symbol = 'CALENDAR_OPTION_BRENT'
    url = f'/data?SYMBOL={symbol}'

    response = client.get(url)

    assert response.status_code == 200

    dataframe = pq.read_table(io.BytesIO(response.data)).to_pandas()
    assert len(dataframe) > 0
