class BlackScholesInputError(Exception):
    def __init__(self, mismatch):
        Exception.__init__(self, mismatch)


class BlackScholesCalculationError(Exception):
    def __init__(self, mismatch):
        Exception.__init__(self, mismatch)
