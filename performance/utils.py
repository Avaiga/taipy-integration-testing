import functools
import time
from dataclasses import dataclass
from datetime import datetime

import pandas as pd


def algorithm(df: pd.DataFrame) -> pd.DataFrame:
    return df


@dataclass
class Row:
    id: int
    age: int
    rating: float


def timer(properties_as_str):
    def __wrapper(f):
        @functools.wraps(f)
        def __execute_wrapper(*args, **kwargs):
            start = time.time()
            result = f(*args, **kwargs)
            end = time.time()
            elapsed = round(end - start, 4)
            dims = ", ".join(properties_as_str)
            print(f'{str(datetime.today())}, {dims}, {f.__name__}, {elapsed}')
            return result

        return __execute_wrapper

    return __wrapper
