# Copyright 2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
import os
import pathlib
import pickle
import random

import taipy.core as tp

from .config import build_pickle_cfg
from .row import Row


class TestPickle:
    PICKLE_DICT_INPUT_PATH = os.path.join(pathlib.Path(__file__).parent.resolve(), "dataset",
                                          "id_age_rating_dict_1000.p")
    PICKLE_LIST_INPUT_PATH = os.path.join(pathlib.Path(__file__).parent.resolve(), "dataset",
                                          "id_age_rating_object_1000.p")
    PICKLE_OUTPUT_PATH = os.path.join(pathlib.Path(__file__).parent.parent.resolve(), "outputs", "output.json")

    ROW_COUNT = 1000

    @staticmethod
    def gen_list_of_dict_input_pickle(path, n):
        data = []
        for i in range(n):
            row = {"id": i + 1, "age": random.randint(10, 99), "rating": round(random.uniform(0, 10), 2)}
            data.append(row)
        pickle.dump(data, open(path, "wb"))

    @staticmethod
    def gen_list_of_objects_input_pickle(path, n):
        data = []
        for i in range(n):
            row = Row(i + 1, random.randint(10, 99), round(random.uniform(0, 10), 2))
            data.append(row)
        pickle.dump(data, open(path, "wb"))

    # gen_list_of_dict_input_pickle(PICKLE_DICT_INPUT_PATH, ROW_COUNT)
    # gen_list_of_objects_input_pickle(PICKLE_LIST_INPUT_PATH, ROW_COUNT)

    with open(PICKLE_DICT_INPUT_PATH, "rb") as f:
        dict_data = pickle.load(f)
    with open(PICKLE_LIST_INPUT_PATH, "rb") as f:
        list_data = pickle.load(f)

    def test_pickle_dict(self):
        self.__test(self.PICKLE_DICT_INPUT_PATH, self.PICKLE_OUTPUT_PATH, self.dict_data)

    def test_pickle_list(self):
        self.__test(self.PICKLE_LIST_INPUT_PATH, self.PICKLE_OUTPUT_PATH, self.list_data)

    def __test(self, input_path, output_path, data):
        scenario_cfg = build_pickle_cfg(input_path, output_path)
        scenario = tp.create_scenario(scenario_cfg)
        in_dn1 = scenario.input_dn_1
        out_dn2 = scenario.output_dn_2
        read_data = in_dn1.read()
        assert len(read_data) == self.ROW_COUNT
        assert read_data == data
        assert out_dn2.read() is None
        out_dn2.write(read_data)
        assert data == out_dn2.read()
        out_dn2.write(None)
        assert out_dn2.read() is None
        scenario.submit()
        assert data == out_dn2.read()
