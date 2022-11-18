import random
import time
import functools
from datetime import datetime


def timer(row_count, exposed_type):
    def __wrapper(f):
        @functools.wraps(f)
        def __execute_wrapper(*args, **kwargs):
            start = time.time()
            result = f(*args, **kwargs)
            end = time.time()
            elapsed = round(end - start, 4)
            print(f'{str(datetime.today())}, {row_count}, {exposed_type}, {f.__name__}, {elapsed}')
            return result
        
        return __execute_wrapper
    return __wrapper


def gen_input_csv(input_folder, rows):
    path = f"{input_folder}/input_{rows}.csv"
    col_names = ["id", "age", "rating"]
    lines = [",".join(col_names)]
    for i in range(rows):
        lines.append(f"{i+1},{random.randint(1,99)},{round(random.uniform(0,10),2)}")
    with open(path, "w+") as f:
        f.write("\n".join(lines))
