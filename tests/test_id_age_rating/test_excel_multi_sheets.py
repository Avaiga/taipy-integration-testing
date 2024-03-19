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
import pytest
import taipy.core as tp

from .row import Row
from .config import build_excel_cfg


class TestExcelMultiSheets:
    XLSX_INPUT_PATH = os.path.join(pathlib.Path(__file__).parent.resolve(), "dataset",
                                   "id_age_rating_1000_multi_sheets_10x100.xlsx")
    XLSX_OUTPUT_PATH = os.path.join(pathlib.Path(__file__).parent.parent.resolve(), "outputs", "output.xlsx")
    ROW_COUNT = 1000
    SHEETS = ["Sheet 0", "Sheet 1", "Sheet 2", "Sheet 3", "Sheet 4", "Sheet 5"]

    def test_excel_multi_sheet_pandas(self):
        pandas_data = pd.read_excel(self.XLSX_INPUT_PATH, sheet_name=self.SHEETS)
        scenario_cfg = build_excel_cfg(self.XLSX_INPUT_PATH, self.XLSX_OUTPUT_PATH, self.SHEETS, "pandas")

        scenario = tp.create_scenario(scenario_cfg)
        in_dn1 = scenario.input_dn_1
        out_dn2 = scenario.output_dn_2

        read_data = in_dn1.read()
        assert len(read_data) == len(self.SHEETS)
        assert all([pandas_data[sheet_name].equals(read_data[sheet_name]) for sheet_name in self.SHEETS])

        assert out_dn2.read() is None
        out_dn2.write(read_data)
        assert len(out_dn2.read()) == len(self.SHEETS)
        assert all([pandas_data[sheet_name].equals(out_dn2.read()[sheet_name]) for sheet_name in self.SHEETS])

        out_dn2.write({sheet_name: pd.DataFrame() for sheet_name in self.SHEETS})

        scenario.submit()
        assert all([pandas_data[sheet_name].equals(out_dn2.read()[sheet_name]) for sheet_name in self.SHEETS])

    @pytest.mark.skip("Writing data from custom exposed type to excel does not work")
    def test_excel_multi_sheet_custom_exposed_type(self):
        pandas_data = pd.read_excel(self.XLSX_INPUT_PATH, sheet_name=self.SHEETS)
        custom_data = {}
        for sheet_name in self.SHEETS:
            rows = []
            for _, row in pandas_data[sheet_name].iterrows():
                rows.append(Row(int(row.id), int(row.age), float(row.rating)))
            custom_data[sheet_name] = rows

        def compare_custom_date(read_data, custom_data):
            return [
                row_1.id == row_2.id and row_1.age == row_2.age and row_1.rating == row_2.rating
                for row_1, row_2 in zip(read_data, custom_data)
            ]

        scenario_cfg = build_excel_cfg(self.XLSX_INPUT_PATH, self.XLSX_OUTPUT_PATH, self.SHEETS, Row)

        scenario = tp.create_scenario(scenario_cfg)
        in_dn1 = scenario.input_dn_1
        out_dn2 = scenario.output_dn_2

        read_data = in_dn1.read()
        assert len(read_data) == len(self.SHEETS)
        assert all(compare_custom_date(read_data[sheet], custom_data[sheet]) for sheet in self.SHEETS)

        out_dn2.write(read_data)  # TODO: Fix this. It does not work to write custom data to excel
        assert len(out_dn2.read()) == len(self.SHEETS)
        assert all(compare_custom_date(custom_data[sheet], out_dn2.read()[sheet]) for sheet in self.SHEETS)

        out_dn2.write(None)
        assert isinstance(out_dn2.read(), list)
        assert len(out_dn2.read()) == 0
        assert all(compare_custom_date(custom_data[sheet], out_dn2.read()[sheet]) for sheet in self.SHEETS)

        scenario.submit()
        assert all(compare_custom_date(custom_data[sheet], out_dn2.read()[sheet]) for sheet in self.SHEETS)

    def test_excel_multi_sheet_numpy(self):
        pandas_data = pd.read_excel(self.XLSX_INPUT_PATH, sheet_name=self.SHEETS)
        numpy_data = {sheet_name: pandas_data[sheet_name].to_numpy() for sheet_name in self.SHEETS}
        scenario_cfg = build_excel_cfg(self.XLSX_INPUT_PATH, self.XLSX_OUTPUT_PATH, self.SHEETS, "numpy")

        scenario = tp.create_scenario(scenario_cfg)
        in_dn1 = scenario.input_dn_1
        out_dn2 = scenario.output_dn_2

        read_data = in_dn1.read()
        assert len(read_data) == len(self.SHEETS)
        assert [np.array_equal(read_data[sheet_name], numpy_data[sheet_name]) for sheet_name in self.SHEETS]

        assert out_dn2.read() is None
        out_dn2.write(read_data)
        assert len(out_dn2.read()) == len(self.SHEETS)
        assert [np.array_equal(read_data[sheet_name], out_dn2.read()[sheet_name]) for sheet_name in self.SHEETS]

        scenario.submit()
        assert [np.array_equal(read_data[sheet_name], out_dn2.read()[sheet_name]) for sheet_name in self.SHEETS]
