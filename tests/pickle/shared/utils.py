from dataclasses import dataclass
import pickle
import random
import time


@dataclass
class Row:
    id: int
    age: int
    rating: float


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


def gen_list_of_dict_input_pickle(path, n):
    print(f"Generating {path} with {n:,} dicts...")
    data = []
    for i in range(n):
        row = {"id": i+1,
               "age": random.randint(10, 99),
               "rating": round(random.uniform(0, 10), 2)
               }
        data.append(row)
    pickle.dump(data, open(path, "wb"))


def gen_list_of_objects_input_pickle(path, n):
    print(f"Generating {path} with {n:,} objects...")
    data = []
    for i in range(n):
        row = Row(i+1, random.randint(10, 99), round(random.uniform(0, 10), 2))
        data.append(row)
    pickle.dump(data, open(path, "wb"))
