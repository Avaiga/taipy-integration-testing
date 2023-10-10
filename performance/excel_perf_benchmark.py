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
import random
import sys
from datetime import datetime
from typing import List

import pandas as pd
import taipy as tp
from data_perf_benchmark import DataPerfBenchmark
from taipy import Config
from utils import Row, algorithm


class ExcelPerfBenchmark(DataPerfBenchmark):
    BENCHMARK_NAME = "EXCEL Data node perf"
    BENCHMARK_REPORT_FILE_NAME = "excel_data_node_benchmark_report.csv"
    HEADERS = ["github_sha", "datetime", "exposed_type", "sheet_counts", "row_counts", "function_name", "time_elapsed"]

    def __init__(self, github_sha: str, row_counts: List[int] = None, report_path: str = None):
        super().__init__(github_sha=github_sha, row_counts=row_counts, report_path=report_path)

        self.sheet_counts = [1, 5]
        sheet_names = [f"Sheet{sheet}" for sheet in range(5)]
        self.prop_dicts = [
            {"exposed_type": "pandas"},
            {"exposed_type": Row},
            {"exposed_type": "numpy"},
            {"exposed_type": "modin"},
            {"exposed_type": "pandas", "sheet_names": sheet_names},
            {"exposed_type": Row, "sheet_names": sheet_names},
            {"exposed_type": "numpy", "sheet_names": sheet_names},
            {"exposed_type": "modin", "sheet_names": sheet_names},
        ]

    def run(self):
        self.log_header()
        with open(self.report_path, "a", encoding="utf-8") as f:
            sys.stdout = f
            if os.path.getsize(self.report_path) == 0:
                print(",".join(self.HEADERS))
            time_start = str(datetime.today())
            for row_count in self.row_counts:
                for sheet_count in self.sheet_counts:
                    self._generate_input_file(row_count, sheet_count)
                    for properties in self._generate_prop_sets():
                        self._run_test(row_count, sheet_count, properties, time_start)
                        self.clean_test_state()

    def _generate_input_file(self, n_rows: int, n_sheets: int):
        if n_sheets < 1:
            raise ValueError(f"Xlsx file must have at least 1 sheet, the n_sheets provided has only {n_sheets} sheets")
        with pd.ExcelWriter(f"{self.input_folder_path}/input_{n_rows}_{n_sheets}_sheets.xlsx") as writer:
            for sheet in range(n_sheets):
                sheet_name = f"Sheet{sheet}"
                rows = []
                for i in range(n_rows):
                    row = {"id": i + 1, "age": random.randint(10, 99), "rating": round(random.uniform(0, 10), 2)}
                    rows.append(row)
                pd.DataFrame(rows).to_excel(writer, sheet_name=sheet_name, index=False)

    def _run_test(self, row_count: int, sheet_count: int, properties, time_start):
        def to_str(properties):
            exposed_type = properties["exposed_type"]
            exposed_type = exposed_type if isinstance(exposed_type, str) else exposed_type.__name__
            return [exposed_type]

        properties_as_str = to_str(properties)
        properties_as_str.append(str(sheet_count))
        properties_as_str.append(str(row_count))
        prefix = "_".join(properties_as_str)
        properties_as_str.insert(0, self.github_sha)
        properties_as_str.insert(1, time_start)

        scenario_cfg = self._generate_configs(prefix, row_count, sheet_count, **properties)
        input_data_node, output_data_node, sequence, scenario = self._generate_entities(prefix, scenario_cfg)
        (
            read_data_node,
            filter_data_node,
            join_filter_data_node,
            write_data_node,
            submit_sequence,
            submit_scenario,
        ) = self._generate_methods(properties_as_str)

        data = read_data_node(input_data_node)
        if input_data_node.properties["exposed_type"] != "numpy":
            filter_data_node(input_data_node)
        if input_data_node.properties["exposed_type"] not in ["numpy", "modin"]:
            join_filter_data_node(input_data_node)
        if output_data_node.properties["exposed_type"] in ["pandas", "modin", "numpy"]:
            write_data_node(output_data_node, data)
        submit_sequence(sequence)
        submit_scenario(scenario)

    def _generate_configs(self, prefix: str, row_count: int, sheet_count: int, **kwargs):
        Config.unblock_update()

        input_datanode_cfg = Config.configure_excel_data_node(
            id=prefix + "_input_datanode",
            path=f"{self.input_folder_path}/input_{row_count}_{sheet_count}_sheets.xlsx",
            **kwargs,
        )
        output_datanode_cfg = Config.configure_excel_data_node(
            id=prefix + "_output_datanode",
            path=f"{self.output_folder_path}/output_{row_count}_{sheet_count}_sheets.xlsx",
            **kwargs,
        )
        task_cfg = Config.configure_task(
            id=prefix + "_task", input=input_datanode_cfg, function=algorithm, output=output_datanode_cfg
        )
        scenario_cfg = Config.configure_scenario(
            id=prefix + "_scenario", task_configs=[task_cfg], sequences={prefix + "_sequence": [task_cfg]}
        )
        return scenario_cfg
