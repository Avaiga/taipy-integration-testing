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

PICKLE_DICT_INPUT_PATH = "tests/shared_test_cases/pickle_files/input_dict_1000.p"
PICKLE_DICT_OUTPUT_PATH = "tests/shared_test_cases/pickle_files/output_dict_1000.p"
PICKLE_LIST_INPUT_PATH = "tests/shared_test_cases/pickle_files/input_object_1000.p"
PICKLE_LIST_OUTPUT_PATH = "tests/shared_test_cases/pickle_files/output_object_1000.p"
ROW_COUNT = 1000


@dataclasses.dataclass
class Row:
    id: int
    age: int
    rating: float


Config.unblock_update()

input_dataset_cfg_1 = Config.configure_pickle_data_node(id="input_pickle_dataset_1", path=PICKLE_DICT_INPUT_PATH)
output_dataset_cfg_1 = Config.configure_pickle_data_node(id="output_pickle_dataset_1", path=PICKLE_DICT_OUTPUT_PATH)
task_cfg_1 = Config.configure_task(id="t1", input=input_dataset_cfg_1, function=algorithm, output=output_dataset_cfg_1)
scenario_cfg_1 = Config.configure_scenario(id="s1", task_configs=[task_cfg_1], frequency=Frequency.DAILY)

input_dataset_cfg_2 = Config.configure_pickle_data_node(id="input_pickle_dataset_2", path=PICKLE_LIST_INPUT_PATH)
output_dataset_cfg_2 = Config.configure_pickle_data_node(id="output_pickle_dataset_2", path=PICKLE_LIST_OUTPUT_PATH)
task_cfg_2 = Config.configure_task(id="t2", input=input_dataset_cfg_2, function=algorithm, output=output_dataset_cfg_2)
scenario_cfg_2 = Config.configure_scenario(id="s2", task_configs=[task_cfg_2], frequency=Frequency.DAILY)
