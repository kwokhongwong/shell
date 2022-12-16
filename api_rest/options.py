from marshmallow import fields, post_load, Schema
from api_rest.request import Request
from api_rest.request_type import RequestType


class OptionPriceRequest(Request):

    def __init__(self, *args, **kwargs):
        super(OptionPriceRequest, self).__init__(
            params=kwargs,
            request_type=RequestType.OPTION_PRICE
        )


class OptionPriceRequestSchema(Schema):

    OPTION_TYPE = fields.Str(required=True)
    X = fields.Float(required=True)
    FS = fields.Float(required=True)
    T = fields.Float(required=True)
    B = fields.Float(required=True)
    R = fields.Float(required=True)
    V = fields.Float(required=True)

    @post_load
    def make_option_price(self, data, **kwargs):
        return OptionPriceRequest(**data)


class CommodityOptionPriceRequest(Request):

    def __init__(self, *args, **kwargs):
        super(CommodityOptionPriceRequest, self).__init__(
            params=kwargs,
            request_type=RequestType.OPTION_PRICE
        )


class CommodityOptionPriceRequestSchema(Schema):

    CONTRACT = fields.Str(required=True)
    EXCHANGE_CODE = fields.Str(required=False, default=None)
    MONTH = fields.Str(required=True)
    YEAR = fields.Str(required=True)
    OPTION_TYPE = fields.Str(required=True)
    STRIKE = fields.Float(required=False)
    LOT_PRICE = fields.Bool(required=False)

    @post_load
    def make_commodity_option_price(self, data, **kwargs):
        from analytics.constants import CONTRACT_DEFAULT_EXCHANGE_MAP, CONTRACT_EXCHANGE_MAP

        try:
            contract = data['CONTRACT']
        except KeyError:
            raise ValueError(f'Unsupported contract {contract}')

        try:
            exchange_code = data['EXCHANGE_CODE']
        except KeyError:
            exchange_code = CONTRACT_DEFAULT_EXCHANGE_MAP[contract]

        try:
            CONTRACT_EXCHANGE_MAP[(contract, exchange_code)]
        except KeyError:
            raise ValueError(f'Unsupported contract {contract}, exchange_code {exchange_code}')

        return CommodityOptionPriceRequest(**data)
