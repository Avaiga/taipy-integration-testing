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

from .row import Row
from .config import build_excel_cfg


class TestExcelMultiSheets:
    XLSX_INPUT_PATH = os.path.join(pathlib.Path(__file__).parent.resolve(), "dataset",
                                   "id_age_rating_1000_single_sheet.xlsx")
    XLSX_OUTPUT_PATH = os.path.join(pathlib.Path(__file__).parent.parent.resolve(), "outputs", "output.xlsx")
    ROW_COUNT = 1000
    SHEET = "Sheet1"

    def test_excel_pandas(self):
        pandas_data = pd.read_excel(self.XLSX_INPUT_PATH)
        scenario_cfg = build_excel_cfg(self.XLSX_INPUT_PATH, self.XLSX_OUTPUT_PATH, self.SHEET, "pandas")

        scenario = tp.create_scenario(scenario_cfg)
        in_dn1 = scenario.input_dn_1
        out_dn2 = scenario.output_dn_2

        read_data = in_dn1.read()
        assert len(read_data) == self.ROW_COUNT
        assert pandas_data.equals(read_data)

        assert out_dn2.read() is None
        out_dn2.write(read_data)
        assert read_data.equals(out_dn2.read())

        out_dn2.write(None)
        assert out_dn2.read().empty

        scenario.submit()
        assert pandas_data.equals(out_dn2.read())

    def test_excel_custom_exposed_type(self):
        custom_data = [Row(int(v.id), int(v.age), float(v.rating)) for i, v in pd.read_excel(
            self.XLSX_INPUT_PATH).iterrows()]

        def compare_custom_date(read_data, custom_data):
            return [
                row_1.id == row_2.id and row_1.age == row_2.age and row_1.rating == row_2.rating
                for row_1, row_2 in zip(read_data, custom_data)
            ]

        scenario_cfg = build_excel_cfg(self.XLSX_INPUT_PATH, self.XLSX_OUTPUT_PATH, self.SHEET, Row)

        scenario = tp.create_scenario(scenario_cfg)
        in_dn1 = scenario.input_dn_1
        out_dn2 = scenario.output_dn_2

        read_data = in_dn1.read()
        assert len(read_data) == self.ROW_COUNT
        assert all(compare_custom_date(read_data, custom_data))

        out_dn2.write(read_data)
        assert len(read_data) == self.ROW_COUNT
        assert all(compare_custom_date(out_dn2.read(), custom_data))

        out_dn2.write(None)
        assert isinstance(out_dn2.read(), list)
        assert len(out_dn2.read()) == 0

        scenario.submit()
        assert all(compare_custom_date(out_dn2.read(), custom_data))

    def test_excel_multi_sheet_numpy(self):
        numpy_data = pd.read_excel(self.XLSX_INPUT_PATH).to_numpy()
        scenario_cfg = build_excel_cfg(self.XLSX_INPUT_PATH, self.XLSX_OUTPUT_PATH, self.SHEET, "numpy")

        scenario = tp.create_scenario(scenario_cfg)
        in_dn1 = scenario.input_dn_1
        out_dn2 = scenario.output_dn_2

        read_data = in_dn1.read()
        assert len(read_data) == self.ROW_COUNT
        assert np.array_equal(read_data, numpy_data)

        assert out_dn2.read() is None
        out_dn2.write(read_data)
        assert np.array_equal(out_dn2.read(), numpy_data)

        out_dn2.write(None)
        assert isinstance(out_dn2.read(), np.ndarray)
        assert out_dn2.read().size == 0

        scenario.submit()
        assert np.array_equal(out_dn2.read(), numpy_data)
