from marshmallow import fields, Schema


class DataRequestSchema(Schema):

    SYMBOL = fields.Str(required=True)
