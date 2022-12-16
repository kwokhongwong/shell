from api_rest.request_type import RequestType
from marshmallow import Schema, fields


class Request:

    def __init__(self, params: dict, request_type: RequestType):
        assert request_type

        self.params = params
        self.request_type = request_type


class RequestSchema(Schema):
    params = fields.Dict()
    request_type = fields.Str()
