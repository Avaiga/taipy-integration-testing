import random
import pickle

from tests.shared_test_cases.pickle_files import Row


def gen_list_of_dict_input_pickle(path, n):
    data = []
    for i in range(n):
        row = {"id": i+1,
               "age": random.randint(10, 99),
               "rating": round(random.uniform(0, 10), 2)
               }
        data.append(row)
    pickle.dump(data, open(path, "wb"))


def gen_list_of_objects_input_pickle(path, n):
    data = []
    for i in range(n):
        row = Row(i+1, random.randint(10, 99), round(random.uniform(0, 10), 2))
        data.append(row)
    pickle.dump(data, open(path, "wb"))
