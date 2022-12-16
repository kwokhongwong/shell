from enum import Enum


class RequestType(Enum):
    DSL = 'DSL'
    MARKET = 'MARKET'
    OPTION_PRICE = 'OPTION_PRICE'
    REF_DATA = 'REF_DATA'
