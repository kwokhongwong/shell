import env
import os
import pandas as pd


class DataAPI:

    @staticmethod
    def persist(symbol: str, dataframe: pd.DataFrame) -> str:
        assert symbol
        assert dataframe is not None

        from werkzeug.datastructures import FileStorage

        data_file_path = os.path.sep.join((env.MARKET_DATA_PATH, f'{symbol}.parquet'))
        if isinstance(dataframe, pd.DataFrame):
            dataframe.to_parquet(path=data_file_path)
        elif isinstance(dataframe, FileStorage):
            dataframe.save(data_file_path)
        else:
            raise ValueError(f'Unsupported object type {type(dataframe)}')

        return f'Market data save successful for symbol {symbol}'

    @staticmethod
    def query(symbol: str) -> pd.DataFrame:
        assert symbol

        data_file_path = os.path.sep.join((env.MARKET_DATA_PATH, f'{symbol}.parquet'))

        return pd.read_parquet(data_file_path)
