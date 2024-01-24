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

from taipy.config import Config
from .algorithms import sum as my_sum
from .algorithms import *

def build_example_config(dataset_csv_path, dataset_excel_path):
    # d1 --- t1
    # |
    # | ---- t2 --- d5 ---|                             -- t10 --- d12
    #        |            |                            /
    # d2 ----             |                           /
    #                     | --- t5 --- d7 --- t7 --- d9 --- t8 --- d10 --- t9 --- d11
    #                     |                 /                |
    # d4 --- |            |                /                 |
    #        |            |     t6 --- d8 -------------------
    # d3 --- t4 --- d6 ---|
    # |
    # |----- t3
    csv_path_sum = os.path.join(pathlib.Path(__file__).parent.parent.resolve(), "./outputs/sum.csv")
    excel_path_sum = os.path.join(pathlib.Path(__file__).parent.parent.resolve(), "./outputs/sum.xlsx")
    csv_path_out = os.path.join(pathlib.Path(__file__).parent.parent.resolve(), "./outputs/res.csv")
    excel_path_out = os.path.join(pathlib.Path(__file__).parent.parent.resolve(), "./outputs/res.xlsx")

    d1 = Config.configure_csv_data_node("d1", default_path=dataset_csv_path)
    d2 = Config.configure_csv_data_node("d2", default_path=dataset_csv_path)
    d3 = Config.configure_excel_data_node(
        "d3",
        default_path=dataset_excel_path,
        sheet_name="Sheet1")
    d4 = Config.configure_excel_data_node(
        "d4",
        default_path=dataset_excel_path,
        sheet_name="Sheet1")

    d5 = Config.configure_csv_data_node("d5", default_path=csv_path_sum)
    d6 = Config.configure_excel_data_node("d6", default_path=excel_path_sum, sheet_name="Sheet1")

    d7 = Config.configure_pickle_data_node("d7")
    d8 = Config.configure_pickle_data_node("d8", default_data=10)
    d9 = Config.configure_pickle_data_node("d9")
    d10 = Config.configure_pickle_data_node("d10")

    d11 = Config.configure_csv_data_node("d11", csv_path_out)
    d12 = Config.configure_excel_data_node("d12", excel_path_out)

    t1 = Config.configure_task("t1", print, input=d1)
    t2 = Config.configure_task("t2", my_sum, input=[d2, d1], output=d5)
    t3 = Config.configure_task("t3", print, input=d3)
    t4 = Config.configure_task("t4", my_sum, input=[d4, d3], output=d6)

    t5 = Config.configure_task("t5", subtract, input=[d5, d6], output=d7)
    t6 = Config.configure_task("t6", return_a_number, output=[d8])
    t7 = Config.configure_task("t7", mult, input=[d7, d8], output=d9)

    t8 = Config.configure_task("t8", divide, input=[d9, d8], output=d10)
    t9 = Config.configure_task("t9", average, input=d10, output=d11)
    t10 = Config.configure_task("t10", average, input=d9, output=d12)

    scenario_config = Config.configure_scenario("scenario", [t1, t2, t3, t4, t5, t6, t7, t8, t9, t10])
    return scenario_config
