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

import os
import pickle

import taipy.core as tp
from taipy.config import Config


def test_pickle_files():
    from tests.shared_test_cases.pickle_files import (
        PICKLE_DICT_INPUT_PATH,
        PICKLE_DICT_OUTPUT_PATH,
        PICKLE_LIST_INPUT_PATH,
        PICKLE_LIST_OUTPUT_PATH,
        ROW_COUNT,
        gen_list_of_dict_input_pickle,
        gen_list_of_objects_input_pickle,
        scenario_cfg_1,
        scenario_cfg_2,
    )

    tp.clean_all_entities_by_version(None)

    # generate 2 pickles files
    gen_list_of_dict_input_pickle(PICKLE_DICT_INPUT_PATH, ROW_COUNT)
    gen_list_of_objects_input_pickle(PICKLE_LIST_INPUT_PATH, ROW_COUNT)

    with open(PICKLE_DICT_INPUT_PATH, "rb") as f:
        dict_data = pickle.load(f)
    with open(PICKLE_LIST_INPUT_PATH, "rb") as f:
        list_data = pickle.load(f)

    # 📝 List of dicts

    scenario_1 = tp.create_scenario(scenario_cfg_1)
    input_data_node_1 = scenario_1.input_pickle_dataset_1
    output_data_node_1 = scenario_1.output_pickle_dataset_1
    pipeline_1 = scenario_1.p1

    read_data_1 = input_data_node_1.read()
    assert len(read_data_1) == ROW_COUNT
    assert read_data_1 == dict_data

    assert output_data_node_1.read() is None
    output_data_node_1.write(read_data_1)
    assert dict_data == output_data_node_1.read()

    output_data_node_1.write(None)
    assert output_data_node_1.read() is None
    pipeline_1.submit()
    assert dict_data == output_data_node_1.read()

    output_data_node_1.write(None)
    assert output_data_node_1.read() is None
    scenario_1.submit()
    assert dict_data == output_data_node_1.read()

    os.remove(PICKLE_DICT_INPUT_PATH)
    os.remove(PICKLE_DICT_OUTPUT_PATH)

    # 📝 List of objects
    scenario_2 = tp.create_scenario(scenario_cfg_2)
    input_data_node_2 = scenario_2.input_pickle_dataset_2
    output_data_node_2 = scenario_2.output_pickle_dataset_2
    pipeline_2 = scenario_2.p2

    read_data_2 = input_data_node_2.read()
    assert len(read_data_2) == ROW_COUNT
    assert read_data_2 == list_data

    assert output_data_node_2.read() is None
    output_data_node_2.write(read_data_2)
    assert list_data == output_data_node_2.read()

    output_data_node_2.write(None)
    assert output_data_node_2.read() is None
    pipeline_2.submit()
    assert list_data == output_data_node_2.read()

    output_data_node_2.write(None)
    assert output_data_node_2.read() is None
    scenario_2.submit()
    assert list_data == output_data_node_2.read()

    os.remove(PICKLE_LIST_INPUT_PATH)
    os.remove(PICKLE_LIST_OUTPUT_PATH)
