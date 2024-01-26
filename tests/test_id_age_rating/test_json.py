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
import json
import os
import pathlib

import taipy.core as tp

from .config import build_json_cfg
from .row import Row, RowDecoder, RowEncoder


class TestJson:
    JSON_INPUT_PATH = os.path.join(pathlib.Path(__file__).parent.resolve(), "dataset", "id_age_rating_1000_dict.json")
    JSON_OBJ_INPUT_PATH = os.path.join(pathlib.Path(__file__).parent.resolve(), "dataset",
                                       "id_age_rating_1000_object.json")
    JSON_OUTPUT_PATH = os.path.join(pathlib.Path(__file__).parent.parent.resolve(), "outputs", "output.json")

    ROW_COUNT = 1000
    SHEET = "Sheet1"

    with open(JSON_INPUT_PATH, "r") as f:
        json_dict_data = json.load(f)
    with open(JSON_OBJ_INPUT_PATH, "r") as f:
        json_object_data = json.load(f, cls=RowDecoder)

    def test_json(self):
        scenario_cfg = build_json_cfg(self.JSON_INPUT_PATH, self.JSON_OUTPUT_PATH)

        scenario = tp.create_scenario(scenario_cfg)
        in_dn1 = scenario.input_dn_1
        out_dn2 = scenario.output_dn_2

        read_data = in_dn1.read()
        assert len(read_data) == self.ROW_COUNT
        assert self.json_dict_data == read_data

        assert out_dn2.read() is None
        out_dn2.write(read_data)
        assert self.json_dict_data == out_dn2.read()

        out_dn2.write(None)
        assert out_dn2.read() is None

        scenario.submit()
        assert self.json_dict_data == out_dn2.read()

    def test_json_with_encoder(self):
        def compare_custom_date(read_data, object_data):
            return [
                isinstance(row_1,
                           Row) and row_1.id == row_2.id and row_1.age == row_2.age and row_1.rating == row_2.rating
                for row_1, row_2 in zip(read_data, object_data)
            ]

        scenario_cfg = build_json_cfg(self.JSON_OBJ_INPUT_PATH, self.JSON_OUTPUT_PATH, RowEncoder, RowDecoder)

        scenario = tp.create_scenario(scenario_cfg)
        in_dn1 = scenario.input_dn_1
        out_dn2 = scenario.output_dn_2

        read_data = in_dn1.read()
        assert len(read_data) == self.ROW_COUNT
        assert all(compare_custom_date(read_data, self.json_object_data))

        assert out_dn2.read() is None
        out_dn2.write(read_data)
        assert all(compare_custom_date(out_dn2.read(), self.json_object_data))

        out_dn2.write(None)
        assert out_dn2.read() is None

        scenario.submit()
        assert all(compare_custom_date(out_dn2.read(), self.json_object_data))
