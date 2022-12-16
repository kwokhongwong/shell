from api import LocalClient as c
from api_rest.data import DataRequestSchema
from api_rest.env import TweakEnvRequestSchema
from api_rest.market import MarketDataSaveSchema
from api_rest.options import CommodityOptionPriceRequestSchema, OptionPriceRequestSchema
from flask import Flask, jsonify, request, Response
from http import HTTPStatus


app = Flask(__name__)


@app.route('/env_variables', methods=['GET'])
def env_variables():

    try:

        return jsonify({'ENV_VARIABLES': c.env_variables()})

    except Exception as e:
        return Response(str(e), status=HTTPStatus.BAD_REQUEST)


@app.route('/tweak_env', methods=['GET'])
def tweak_env():

    try:

        tweak_env_schema = TweakEnvRequestSchema()
        tweak_env_request = tweak_env_schema.load(request.args)

        key = tweak_env_request["KEY"]
        value = tweak_env_request["VALUE"]
        c.tweak_env(key=key, value=value)

        return Response(
            f'Env tweaked successful for key={key}, value={value}',
            status=HTTPStatus.OK
        )

    except Exception as e:
        return Response(str(e), status=HTTPStatus.BAD_REQUEST)


@app.route('/save', methods=['POST'])
def save():

    try:
        market_data_save_schema = MarketDataSaveSchema()
        market_upload_request = market_data_save_schema.load(request.args)

        if request.files:

            file = request.files['file']
            c.save(symbol=market_upload_request["SYMBOL"], dataframe=file)

            return Response(
                f'Market data save successful for symbol {market_upload_request["SYMBOL"]}',
                status=HTTPStatus.OK
            )

        else:

            return Response(
                f'Missing file object to save for symbol {market_upload_request["SYMBOL"]}',
                status=HTTPStatus.BAD_REQUEST
            )

    except Exception as e:
        return Response(str(e), status=HTTPStatus.BAD_REQUEST)


@app.route('/data', methods=['GET'])
def data():

    import pyarrow as pa
    import pyarrow.parquet as pq

    try:

        data_request_schema = DataRequestSchema()
        data_request = data_request_schema.load(request.args)

        dataframe = c.data(symbol=data_request['SYMBOL'])
        table = pa.Table.from_pandas(dataframe, preserve_index=True)
        buffer_output_stream = pa.BufferOutputStream()
        pq.write_table(table, buffer_output_stream, compression='snappy')

    except Exception as e:
        return Response(str(e), status=HTTPStatus.BAD_REQUEST)

    return Response(buffer_output_stream.getvalue().to_pybytes(), HTTPStatus.OK)


@app.route('/symbols', methods=['GET'])
def symbols():

    try:

        return jsonify({'SYMBOLS': c.symbols()})

    except Exception as e:
        return Response(str(e), status=HTTPStatus.BAD_REQUEST)


@app.route('/option_price', methods=['GET'])
def option_price():

    try:

        option_price_request = OptionPriceRequestSchema().load(request.args)

        _option_price = c.option_price(
            option_type=option_price_request.params['OPTION_TYPE'],
            x=option_price_request.params['X'],
            fs=option_price_request.params['FS'],
            t=option_price_request.params['T'],
            b=option_price_request.params['B'],
            r=option_price_request.params['R'],
            v=option_price_request.params['V']
        )

    except Exception as e:
        return Response(str(e), status=HTTPStatus.BAD_REQUEST)

    return Response(str(_option_price), status=HTTPStatus.OK)


@app.route('/option_greeks', methods=['GET'])
def option_greeks():

    try:

        option_price_request = OptionPriceRequestSchema().load(request.args)

        _option_greeks = c.option_greeks(
            option_type=option_price_request.params['OPTION_TYPE'],
            x=option_price_request.params['X'],
            fs=option_price_request.params['FS'],
            t=option_price_request.params['T'],
            b=option_price_request.params['B'],
            r=option_price_request.params['R'],
            v=option_price_request.params['V']
        )

    except Exception as e:
        return Response(str(e), status=HTTPStatus.BAD_REQUEST)

    return Response(str(_option_greeks), status=HTTPStatus.OK)


@app.route('/commodity_option_price', methods=['GET'])
def commodity_option_price():

    from analytics.constants import CONTRACT_DEFAULT_EXCHANGE_MAP

    try:

        option_price_request = CommodityOptionPriceRequestSchema().load(request.args)
        contract = option_price_request.params['CONTRACT'].upper()

        _option_price = c.commodity_option_price(
            contract=contract,
            exchange_code=option_price_request.params.get('EXCHANGE_CODE', CONTRACT_DEFAULT_EXCHANGE_MAP[contract]),
            month=option_price_request.params['MONTH'],
            year=option_price_request.params['YEAR'],
            option_type=option_price_request.params['OPTION_TYPE'],
            strike=option_price_request.params.get('STRIKE', None),
            lot_price=option_price_request.params.get('LOT_PRICE', False)
        )

    except Exception as e:
        return Response(str(e), status=HTTPStatus.BAD_REQUEST)

    return Response(str(_option_price), status=HTTPStatus.OK)


@app.route('/commodity_option_greeks', methods=['GET'])
def commodity_option_greeks():

    from analytics.constants import CONTRACT_DEFAULT_EXCHANGE_MAP

    try:

        option_price_request = CommodityOptionPriceRequestSchema().load(request.args)
        contract = option_price_request.params['CONTRACT'].upper()

        _option_greeks = c.commodity_option_greeks(
            contract=contract,
            exchange_code=option_price_request.params.get('EXCHANGE_CODE', CONTRACT_DEFAULT_EXCHANGE_MAP[contract]),
            month=option_price_request.params['MONTH'],
            year=option_price_request.params['YEAR'],
            option_type=option_price_request.params['OPTION_TYPE'],
            strike=option_price_request.params.get('STRIKE', None)
        )

    except Exception as e:
        return Response(str(e), status=HTTPStatus.BAD_REQUEST)

    return Response(str(_option_greeks), status=HTTPStatus.OK)


if __name__ == "__main__":
    app.run(debug=True)
