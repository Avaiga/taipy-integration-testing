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

import modin.pandas as modin_pd
import numpy as np
import pandas as pd
import taipy.core as tp
from taipy.config import Config


def test_csv():
    from tests.shared_test_cases.csv_files.config import (
        CSV_INPUT_PATH,
        CSV_OUTPUT_PATH,
        ROW_COUNT,
        Row,
        scenario_cfg,
        scenario_cfg_2,
        scenario_cfg_3,
        scenario_cfg_4,
    )

    tp.clean_all_entities_by_version(None)

    pandas_data = pd.read_csv(CSV_INPUT_PATH)
    numpy_data = pandas_data.to_numpy()
    modin_data = modin_pd.read_csv(CSV_INPUT_PATH)
    custom_data = [Row(int(v.id), int(v.age), float(v.rating)) for i, v in pd.read_csv(CSV_INPUT_PATH).iterrows()]

    # 📊 Without exposed type (pandas is the default exposed type)

    scenario_1 = tp.create_scenario(scenario_cfg)
    input_data_node_1 = scenario_1.input_csv_dataset_1
    output_data_node_1 = scenario_1.output_csv_dataset_1

    read_data_1 = input_data_node_1.read()
    assert len(read_data_1) == ROW_COUNT
    assert pandas_data.equals(read_data_1)

    assert output_data_node_1.read() is None
    output_data_node_1.write(read_data_1)
    assert pandas_data.equals(output_data_node_1.read())

    output_data_node_1.write(None)
    assert output_data_node_1.read().empty

    scenario_1.submit()
    assert pandas_data.equals(output_data_node_1.read())

    os.remove(CSV_OUTPUT_PATH)

    # 📊 With custom class as exposed type

    def compare_custom_date(read_data, custom_data):
        return [
            row_1.id == row_2.id and row_1.age == row_2.age and row_1.rating == row_2.rating
            for row_1, row_2 in zip(read_data, custom_data)
        ]

    scenario_2 = tp.create_scenario(scenario_cfg_2)
    input_data_node_2 = scenario_2.input_csv_dataset_2
    output_data_node_2 = scenario_2.output_csv_dataset_2

    read_data_2 = input_data_node_2.read()
    assert len(read_data_2) == ROW_COUNT
    assert all(compare_custom_date(read_data_2, custom_data))

    output_data_node_2.write(read_data_2)
    assert len(read_data_2) == ROW_COUNT
    assert all(compare_custom_date(output_data_node_2.read(), custom_data))

    output_data_node_2.write(None)
    assert isinstance(output_data_node_2.read(), list)
    assert len(output_data_node_2.read()) == 0

    scenario_2.submit()
    assert all(compare_custom_date(output_data_node_2.read(), custom_data))

    os.remove(CSV_OUTPUT_PATH)

    # 📊 With numpy as exposed type
    scenario_3 = tp.create_scenario(scenario_cfg_3)
    input_data_node_3 = scenario_3.input_csv_dataset_3
    output_data_node_3 = scenario_3.output_csv_dataset_3

    read_data_3 = input_data_node_3.read()
    assert len(read_data_3) == ROW_COUNT
    assert np.array_equal(read_data_3, numpy_data)

    assert output_data_node_3.read() is None
    output_data_node_3.write(read_data_3)
    assert np.array_equal(output_data_node_3.read(), numpy_data)

    output_data_node_3.write(None)
    assert isinstance(output_data_node_3.read(), np.ndarray)
    assert output_data_node_3.read().size == 0

    scenario_3.submit()
    assert np.array_equal(output_data_node_3.read(), numpy_data)

    os.remove(CSV_OUTPUT_PATH)

    # 📊 With modin as exposed type
    scenario_4 = tp.create_scenario(scenario_cfg_4)
    input_data_node_4 = scenario_4.input_csv_dataset_4
    output_data_node_4 = scenario_4.output_csv_dataset_4

    read_data_4 = input_data_node_4.read()
    assert len(read_data_4) == ROW_COUNT
    assert all(modin_data._to_pandas() == read_data_4._to_pandas())

    assert output_data_node_4.read() is None
    output_data_node_4.write(read_data_4)
    assert all(modin_data._to_pandas() == output_data_node_4.read()._to_pandas())

    output_data_node_4.write(None)
    assert output_data_node_4.read().empty

    scenario_4.submit()
    assert all(modin_data._to_pandas() == output_data_node_4.read()._to_pandas())

    os.remove(CSV_OUTPUT_PATH)
