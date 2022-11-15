import random
import time
import pandas as pd


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


def get_input_data(n_rows: int, n_sheets: int):
    data = {}
    n_rows //= n_sheets
    for sheet in range(n_sheets):
        sheet_name = f"Sheet {sheet}"
        rows = []
        for i in range(n_rows):
            row = {"id": i+1,
                   "age": random.randint(10, 99),
                   "rating": round(random.uniform(0, 10), 2)
                   }
            rows.append(row)
        data[sheet_name] = pd.DataFrame(rows)
    if (len(data.values()) == 1):
        return list(data.values())[0]
    return data
