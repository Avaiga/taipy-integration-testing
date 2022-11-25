import functools
import time
from dataclasses import dataclass
from datetime import datetime
import json
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

class RowEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Row):
            return {"id": obj.id, "age": obj.age, "rating": obj.rating, "__type__": "Row"}
        return json.JSONEncoder.default(self, obj)


class RowDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(
            self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, d):
        if "__type__" in d and d["__type__"] == "Row":
            return Row(d["id"], d["age"], d["rating"])