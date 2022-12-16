from marshmallow import fields, Schema


class MarketDataSaveSchema(Schema):

    SYMBOL = fields.Str(required=True)
    FILE_EXTENSION = fields.Str(required=True)
