# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import pickle
import random

from tests.shared_test_cases.pickle_files import Row


def gen_list_of_dict_input_pickle(path, n):
    data = []
    for i in range(n):
        row = {"id": i + 1, "age": random.randint(10, 99), "rating": round(random.uniform(0, 10), 2)}
        data.append(row)
    pickle.dump(data, open(path, "wb"))


def gen_list_of_objects_input_pickle(path, n):
    data = []
    for i in range(n):
        row = Row(i + 1, random.randint(10, 99), round(random.uniform(0, 10), 2))
        data.append(row)
    pickle.dump(data, open(path, "wb"))
