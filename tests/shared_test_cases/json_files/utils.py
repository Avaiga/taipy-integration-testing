# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import json
import random
import time
from dataclasses import dataclass


@dataclass
class Row:
    id: int
    age: int
    rating: float


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


def timer(f):
    def wrapper(*args, **kwargs):
        print(f"⏳ {f.__name__}")
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        elapsed = round(end - start, 4)
        print(f"\t✔️ {elapsed} seconds")
        return result

    return wrapper


def get_list_of_dicts(n):
    data = []
    for i in range(n):
        row = {"id": i + 1, "age": random.randint(10, 99), "rating": round(random.uniform(0, 10), 2)}
        data.append(row)
    return data


def get_list_of_objects(n):
    data = []
    for i in range(n):
        row = Row(i + 1, random.randint(10, 99), round(random.uniform(0, 10), 2))
        data.append(row)
    return data
