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

import numpy as np
import pandas as pd
import taipy.core as tp

from .config import build_csv_config
from .row import Row


class TestCSV:
    CSV_INPUT_PATH = os.path.join(pathlib.Path(__file__).parent.resolve(), "dataset", "id_age_rating_1000.csv")
    CSV_OUTPUT_PATH = os.path.join(pathlib.Path(__file__).parent.parent.resolve(), "outputs", "output.csv")
    ROW_COUNT = 1000

    pandas_data = pd.read_csv(CSV_INPUT_PATH)
    numpy_data = pandas_data.to_numpy()
    custom_data = [Row(int(v.id), int(v.age), float(v.rating)) for i, v in pd.read_csv(CSV_INPUT_PATH).iterrows()]

    def test_csv_default_exposed_type(self):
        # Without exposed type (pandas is the default exposed type)
        scenario_cfg = build_csv_config(self.CSV_INPUT_PATH, self.CSV_OUTPUT_PATH, "pandas")

        scenario = tp.create_scenario(scenario_cfg)
        input_dn_1 = scenario.input_dn_1
        output_dn_2 = scenario.output_dn_2

        read_input_dn_1 = input_dn_1.read()
        assert len(read_input_dn_1) == self.ROW_COUNT
        assert self.pandas_data.equals(read_input_dn_1)

        assert output_dn_2.read() is None
        output_dn_2.write(read_input_dn_1)
        assert self.pandas_data.equals(output_dn_2.read())

        output_dn_2.write(None)
        assert output_dn_2.read().empty

        scenario.submit()
        assert self.pandas_data.equals(output_dn_2.read())

        os.remove(self.CSV_OUTPUT_PATH)

    def test_csv_custom_exposed_type(self):
        scenario_cfg = build_csv_config(self.CSV_INPUT_PATH, self.CSV_OUTPUT_PATH, Row)

        def compare_custom_date(read_data, custom_data):
            return [
                row_1.id == row_2.id and row_1.age == row_2.age and row_1.rating == row_2.rating
                for row_1, row_2 in zip(read_data, custom_data)
            ]

        scenario = tp.create_scenario(scenario_cfg)
        input_dn_1 = scenario.input_dn_1
        output_dn_2 = scenario.output_dn_2

        read_data_2 = input_dn_1.read()
        assert len(read_data_2) == self.ROW_COUNT
        assert all(compare_custom_date(read_data_2, self.custom_data))

        output_dn_2.write(read_data_2)
        assert len(read_data_2) == self.ROW_COUNT
        assert all(compare_custom_date(output_dn_2.read(), self.custom_data))

        output_dn_2.write(None)
        assert isinstance(output_dn_2.read(), list)
        assert len(output_dn_2.read()) == 0

        scenario.submit()
        assert all(compare_custom_date(output_dn_2.read(), self.custom_data))

        os.remove(self.CSV_OUTPUT_PATH)

    def test_csv_numpy_exposed_type(self):
        scenario_cfg = build_csv_config(self.CSV_INPUT_PATH, self.CSV_OUTPUT_PATH, "numpy")
        scenario = tp.create_scenario(scenario_cfg)
        input_dn_1 = scenario.input_dn_1
        output_dn_2 = scenario.output_dn_2

        read_data = input_dn_1.read()
        assert len(read_data) == self.ROW_COUNT
        assert np.array_equal(read_data, self.numpy_data)

        assert output_dn_2.read() is None
        output_dn_2.write(read_data)
        assert np.array_equal(output_dn_2.read(), self.numpy_data)

        output_dn_2.write(None)
        assert isinstance(output_dn_2.read(), np.ndarray)
        assert output_dn_2.read().size == 0

        scenario.submit()
        assert np.array_equal(output_dn_2.read(), self.numpy_data)
        os.remove(self.CSV_OUTPUT_PATH)

