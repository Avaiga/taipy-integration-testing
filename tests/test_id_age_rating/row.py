import dataclasses
import json
from random import random


@dataclasses.dataclass
class Row:
    id: int
    age: int
    rating: float

    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                setattr(self, field.name, field.type(value))


class RowEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Row):
            return {"id": obj.id, "age": obj.age, "rating": obj.rating, "__type__": "Row"}
        return json.JSONEncoder.default(self, obj)


class RowDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, d):
        if "__type__" in d and d["__type__"] == "Row":
            return Row(d["id"], d["age"], d["rating"])
