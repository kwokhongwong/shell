FUTURES_DELIVERY_MAP = {
    'JAN': 'F',
    'FEB': 'G',
    'MAR': 'H',
    'APR': 'J',
    'MAY': 'K',
    'JUN': 'M',
    'JUL': 'N',
    'AUG': 'Q',
    'SEP': 'U',
    'OCT': 'V',
    'NOV': 'X',
    'DEC': 'Z'
}


# (CONTRACT, EXCHANGE_CODE): (OPTIONS_CODE, FUTURES_CODE, LOT_SIZE)
CONTRACT_EXCHANGE_MAP = {
    ('BRENT', 'ICE'): ('B', 'B', 1000),
    ('WTI', 'NYM'): ('CL', 'CL', 1000),
    ('WTI', 'ICE'): ('T', 'T', 1000),
    ('HH', 'NYM'): ('NG', 'NG', 10000),
}


CONTRACT_DEFAULT_EXCHANGE_MAP = {
    'BRENT': 'ICE',
    'WTI': 'NYM',
    'HH': 'NYM'
}


class BlackScholesLimits:

    MAX32 = 2147483248.0

    MIN_T = 1.0 / 1000.0  # requires some time left before expiration
    MIN_X = 0.01
    MIN_FS = 0.01

    # Volatility smaller than 0.5% causes American Options calculations
    # to fail (Number to large errors).
    # GBS() should be OK with any positive number. Since vols less
    # than 0.5% are expected to be extremely rare, and most likely bad inputs,
    # _gbs() is assigned this limit too
    MIN_V = 0.005

    MAX_T = 100
    MAX_X = MAX32
    MAX_FS = MAX32

    # This model will work with higher values for b, r, and V. However, such values are extremely uncommon.
    # To catch some common errors, interest rates and volatility is capped to 100%
    # This reason for 1 (100%) is mostly to cause the library to throw an exceptions
    # if a value like 15% is entered as 15 rather than 0.15)
    MIN_b = -1
    MIN_r = -1

    MAX_b = 1
    MAX_r = 1
    MAX_V = 1
