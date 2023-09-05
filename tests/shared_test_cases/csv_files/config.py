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

import dataclasses

from taipy.config.common.frequency import Frequency
from taipy.config.config import Config

from .algorithms import algorithm

CSV_INPUT_PATH = "tests/shared_test_cases/csv_files/input_1000.csv"
CSV_OUTPUT_PATH = "tests/shared_test_cases/csv_files/output_1000.csv"
ROW_COUNT = 1000


@dataclasses.dataclass
class Row:
    id: int
    age: int
    rating: float

    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                setattr(self, field.name, field.type(value))


Config.unblock_update()
# Config for Pandas
input_dataset_cfg = Config.configure_csv_data_node(id="input_csv_dataset_1", path=CSV_INPUT_PATH, has_header=True)
output_dataset_cfg = Config.configure_csv_data_node(id="output_csv_dataset_1", path=CSV_OUTPUT_PATH, has_header=True)
task_cfg = Config.configure_task(id="t1", input=input_dataset_cfg, function=algorithm, output=output_dataset_cfg)
scenario_cfg = Config.configure_scenario(id="s1", task_configs=[task_cfg], frequency=Frequency.DAILY)

# Config for Custom class
input_dataset_cfg_2 = Config.configure_csv_data_node(
    id="input_csv_dataset_2", path=CSV_INPUT_PATH, has_header=True, exposed_type=Row
)
output_dataset_cfg_2 = Config.configure_csv_data_node(
    id="output_csv_dataset_2", path=CSV_OUTPUT_PATH, has_header=True, exposed_type=Row
)
task_cfg_2 = Config.configure_task(id="t2", input=input_dataset_cfg_2, function=algorithm, output=output_dataset_cfg_2)
scenario_cfg_2 = Config.configure_scenario(id="s2", task_configs=[task_cfg_2], frequency=Frequency.DAILY)

# Config for Numpy
input_dataset_cfg_3 = Config.configure_csv_data_node(
    id="input_csv_dataset_3", path=CSV_INPUT_PATH, has_header=True, exposed_type="numpy"
)
output_dataset_cfg_3 = Config.configure_csv_data_node(
    id="output_csv_dataset_3", path=CSV_OUTPUT_PATH, has_header=True, exposed_type="numpy"
)
task_cfg_3 = Config.configure_task(id="t3", input=input_dataset_cfg_3, function=algorithm, output=output_dataset_cfg_3)
scenario_cfg_3 = Config.configure_scenario(id="s3", task_configs=[task_cfg_3], frequency=Frequency.DAILY)

# Config for Modin
input_dataset_cfg_4 = Config.configure_csv_data_node(
    id="input_csv_dataset_4", path=CSV_INPUT_PATH, has_header=True, exposed_type="modin"
)
output_dataset_cfg_4 = Config.configure_csv_data_node(
    id="output_csv_dataset_4", path=CSV_OUTPUT_PATH, has_header=True, exposed_type="modin"
)
task_cfg_4 = Config.configure_task(id="t4", input=input_dataset_cfg_4, function=algorithm, output=output_dataset_cfg_4)
scenario_cfg_4 = Config.configure_scenario(id="s4", task_configs=[task_cfg_4], frequency=Frequency.DAILY)
