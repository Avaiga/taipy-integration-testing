import functools
import time
import dataclasses
from datetime import datetime
import json
import pandas as pd


def algorithm(df: pd.DataFrame) -> pd.DataFrame:
    return df


@dataclasses.dataclass(eq=True, unsafe_hash=True)
class Row:
    id: int
    age: int
    rating: float

    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                try:
                    setattr(self, field.name, field.type(value))
                except ValueError:
                    raise ValueError(f'Expected {field.name} to be {field.type}, '
                                    f'got {repr(value)}')
 

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
