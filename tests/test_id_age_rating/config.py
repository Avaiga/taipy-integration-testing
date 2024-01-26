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

from taipy.config.common.frequency import Frequency
from taipy.config.config import Config

from .algorithms import algorithm


def build_csv_config(csv_input_path, csv_output_path, exposed_type):
    # input_dn_1 ---> t1 ---> output_dn_2
    input_dn_1_cfg = Config.configure_csv_data_node(
        id="input_dn_1", default_path=csv_input_path, has_header=True, exposed_type=exposed_type)
    output_dn_2_cfg = Config.configure_csv_data_node(
        id="output_dn_2", default_path=csv_output_path, has_header=True, exposed_type=exposed_type)
    t1_cfg = Config.configure_task(id="t1", input=input_dn_1_cfg, function=algorithm, output=output_dn_2_cfg)
    return Config.configure_scenario(id="scenario", task_configs=[t1_cfg], frequency=Frequency.DAILY)


def build_excel_cfg(excel_input_path, excel_output_path, sheet_name, exposed_type):
    # input_dn_1 ---> t1 ---> output_dn_2
    input_dn_1_cfg = Config.configure_excel_data_node(
        id="input_dn_1",
        default_path=excel_input_path,
        has_header=True,
        sheet_name=sheet_name,
        exposed_type=exposed_type
    )
    output_dn_2_cfg = Config.configure_excel_data_node(
        id="output_dn_2",
        default_path=excel_output_path,
        has_header=True,
        sheet_name=sheet_name,
        exposed_type=exposed_type
    )
    t1_cfg = Config.configure_task(id="t1", input=input_dn_1_cfg, function=algorithm, output=output_dn_2_cfg)
    return Config.configure_scenario(id="scenario", task_configs=[t1_cfg], frequency=Frequency.DAILY)


def build_json_cfg(input_path, output_path, encoder=None, decoder=None):
    in_dn_1_cfg = Config.configure_json_data_node(id="input_dn_1", default_path=input_path, encoder=encoder,
                                                  decoder=decoder)
    out_dn_2_cfg = Config.configure_json_data_node(id="output_dn_2", default_path=output_path, encoder=encoder,
                                                   decoder=decoder)
    t1_cfg = Config.configure_task(id="t1", input=in_dn_1_cfg, function=algorithm, output=out_dn_2_cfg)
    return Config.configure_scenario(id="scenario", task_configs=[t1_cfg], frequency=Frequency.DAILY)


def build_pickle_cfg(input_path, output_path):
    in_dn_1_cfg = Config.configure_data_node(id="input_dn_1", default_path=input_path)
    out_dn_2_cfg = Config.configure_data_node(id="output_dn_2", default_path=output_path)
    t1_cfg = Config.configure_task(id="t1", input=in_dn_1_cfg, function=algorithm, output=out_dn_2_cfg)
    return Config.configure_scenario(id="scenario", task_configs=[t1_cfg], frequency=Frequency.DAILY)
