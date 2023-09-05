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
import os

import taipy.core as tp
from taipy.config import Config


def test_json():
    from tests.shared_test_cases.json_files import (
        JSON_DICT_INPUT_PATH,
        JSON_DICT_OUTPUT_PATH,
        JSON_OBJECT_INPUT_PATH,
        JSON_OBJECT_OUTPUT_PATH,
        ROW_COUNT,
        Row,
        RowDecoder,
        scenario_cfg_1,
        scenario_cfg_2,
    )

    tp.clean_all_entities_by_version(None)

    with open(JSON_DICT_INPUT_PATH, "r") as f:
        json_dict_data = json.load(f)
    with open(JSON_OBJECT_INPUT_PATH, "r") as f:
        json_object_data = json.load(f, cls=RowDecoder)

    # 📝 Without encoder / decoder

    scenario_1 = tp.create_scenario(scenario_cfg_1)
    input_data_node_1 = scenario_1.input_json_dataset_1
    output_data_node_1 = scenario_1.output_json_dataset_1

    read_data_1 = input_data_node_1.read()
    assert len(read_data_1) == ROW_COUNT
    assert json_dict_data == read_data_1

    assert output_data_node_1.read() is None
    output_data_node_1.write(read_data_1)
    assert json_dict_data == output_data_node_1.read()

    output_data_node_1.write(None)
    assert output_data_node_1.read() is None

    scenario_1.submit()
    assert json_dict_data == output_data_node_1.read()

    os.remove(JSON_DICT_OUTPUT_PATH)

    # 📝 With encoder / decoder

    def compare_custom_date(read_data, object_data):
        return [
            isinstance(row_1, Row) and row_1.id == row_2.id and row_1.age == row_2.age and row_1.rating == row_2.rating
            for row_1, row_2 in zip(read_data, object_data)
        ]

    scenario_2 = tp.create_scenario(scenario_cfg_2)
    input_data_node_2 = scenario_2.input_json_dataset_2
    output_data_node_2 = scenario_2.output_json_dataset_2

    read_data_2 = input_data_node_2.read()
    assert len(read_data_2) == ROW_COUNT
    assert all(compare_custom_date(read_data_2, json_object_data))

    assert output_data_node_2.read() is None
    output_data_node_2.write(read_data_2)
    assert all(compare_custom_date(output_data_node_2.read(), json_object_data))

    output_data_node_2.write(None)
    assert output_data_node_2.read() is None

    scenario_2.submit()
    assert all(compare_custom_date(output_data_node_2.read(), json_object_data))

    os.remove(JSON_OBJECT_OUTPUT_PATH)
