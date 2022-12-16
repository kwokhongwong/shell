from marshmallow import fields, Schema


class TweakEnvRequestSchema(Schema):

    KEY = fields.Str(required=True)
    VALUE = fields.Str(required=True)
