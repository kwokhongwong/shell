import os
from analytics.constants import CONTRACT_EXCHANGE_MAP, FUTURES_DELIVERY_MAP
from market.etl_option_expiries import CMEOptionExpiriesAdapter, ICEOptionExpiriesAdapter
from market.etl_yield_curve import FEDUSTAdapter


import ray
ray.init()


use_local_client = True
save = True


# ICE EU Style Brent Option Expiries
ICEOptionExpiriesAdapter(
    symbol='CALENDAR_OPTION_BRENT',
    url='./notebooks/ProductSpecExpiryDates_BRENT_OPTIONS.csv',
    use_local_client=use_local_client
).run(save=save)


# ICE EU Style WTI Option Expiries
ICEOptionExpiriesAdapter(
    symbol='CALENDAR_OPTION_WTI',
    url='./notebooks/ProductSpecExpiryDates_WTI_OPTIONS.csv',
    use_local_client=use_local_client
).run(save=save)


# CME EU Style HH Option Expiries
CMEOptionExpiriesAdapter(
    symbol='CALENDAR_OPTION_HH',
    url='./notebooks/product-calendar_HH_OPTIONS.xls',
    use_local_client=use_local_client
).run(save=save)


# Fed Reserve US Treasury Constant Maturity
FEDUSTAdapter(
    symbol='RIFLGFC',
    url='./notebooks/FRB_H15.csv',
    use_local_client=use_local_client
).run(save=save)


@ray.remote
def load_quandl_owf_implied_vols(
        contract: str,
        exchange_code: str,
        futures_code: str,
        options_code: str,
        year: str,
        month: str,
        url: str,
        save: bool,
        expiration: str,
        python_path: str
):
    assert contract
    assert exchange_code
    assert futures_code
    assert options_code
    assert year
    assert month
    assert url
    assert expiration
    assert python_path

    import sys
    sys.path.insert(0, os.path.abspath(python_path))

    from market.etl_implied_vols import QuandlOWFImpliedVolsAdapter

    params = {
        'EXCHANGE_CODE': exchange_code,
        'FUTURES_CODE': futures_code,
        'OPTIONS_CODE': options_code,
        'YEAR': year,
        'MONTH': month
    }

    symbol = f'{contract}_{exchange_code}_{futures_code}_{options_code}_{expiration}_IVM'

    try:
        return QuandlOWFImpliedVolsAdapter(
            symbol=symbol,
            url=url,
            use_local_client=use_local_client,
            params=params
        ).run(save=save)
    except:
        return


ray_ids = []
url = f'https://data.nasdaq.com/api/v3/datasets/OWF'
python_path = os.path.sep.join((os.getcwd().split(os.path.sep)[:-1]))
for (contract, exchange_code, __), (futures_code, options_code) in CONTRACT_EXCHANGE_MAP.items():

    for year in ('2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030'):

        for month in ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'):
            expiration = f'{FUTURES_DELIVERY_MAP[month]}{year}'
            ray_ids.append(
                load_quandl_owf_implied_vols.remote(
                    contract=contract,
                    exchange_code=exchange_code,
                    futures_code=futures_code,
                    options_code=options_code,
                    year=year,
                    month=month,
                    url=url,
                    save=True,
                    expiration=expiration,
                    python_path=python_path
                )
            )

ray.get(ray_ids)
