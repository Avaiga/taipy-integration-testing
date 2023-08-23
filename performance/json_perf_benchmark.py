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
import json
import random
import sys
from typing import Dict, List
from datetime import datetime

import taipy as tp
from data_perf_benchmark import DataPerfBenchmark
from taipy import Config
from utils import Row, RowDecoder, RowEncoder, algorithm


class JsonPerfBenchmark(DataPerfBenchmark):
    BENCHMARK_NAME = "JSON Data node perf"
    BENCHMARK_REPORT_FILE_NAME = "json_data_node_benchmark_report.csv"
    HEADERS = ['github_sha', 'datetime', 'exposed_type', 'row_counts', 'function_name', 'time_elapsed']

    def __init__(self, github_sha: str, row_counts: List[int] = None, report_path: str = None):
        super().__init__(github_sha=github_sha, row_counts=row_counts, report_path=report_path)
        self.type_formats = ["list_dict", "list_object"]
        self.prop_dicts: List[Dict] = [
            {},
            {"encoder": RowEncoder, "decoder": RowDecoder},
        ]

    def run(self):
        self.log_header()
        with open(self.report_path, "a", encoding="utf-8") as f:
            sys.stdout = f
            if os.path.getsize(self.report_path) == 0:
                print(','.join(self.HEADERS))
            time_start = str(datetime.today())
            for row_count in self.row_counts:
                for type_format, properties in zip(self.type_formats, self._generate_prop_sets()):
                    self._generate_input_file(row_count, type_format)
                    self._run_test(row_count, type_format, properties, time_start)
                    self.clean_test_state()

    @staticmethod
    def __gen_list_of_dict_input_json(n):
        data = []
        for i in range(n):
            row = {"id": i + 1, "age": random.randint(10, 99), "rating": round(random.uniform(0, 10), 2)}
            data.append(row)
        return data

    @staticmethod
    def __gen_list_of_objects_input_json(n):
        data = []
        for i in range(n):
            row = Row(i + 1, random.randint(10, 99), round(random.uniform(0, 10), 2))
            data.append(row)
        return data

    def _generate_input_file(self, rows, type_format: str):
        path = f"{self.input_folder_path}/input_{type_format}_{rows}.json"
        if type_format == "list_dict":
            data = self.__gen_list_of_dict_input_json(rows)
            encoder = None
        if type_format == "list_object":
            data = self.__gen_list_of_objects_input_json(rows)
            encoder = RowEncoder
        with open(path, "w") as f:
            json.dump(data, f, indent=4, cls=encoder)

    def _run_test(self, row_count: int, type_format: str, properties, time_start):
        def to_str(val):
            return "with_custom_encoder" if val else "without_custom_encoder"

        properties_as_str = [to_str(properties)]
        properties_as_str.append(str(row_count))
        prefix = "_".join(properties_as_str)
        properties_as_str.insert(0, self.github_sha)
        properties_as_str.insert(1, time_start)

        scenario_cfg = self._generate_configs(prefix, row_count, type_format, **properties)
        input_data_node, output_data_node, sequence, scenario = self._generate_entities(prefix, scenario_cfg)
        read_data_node, _, _, write_data_node, submit_sequence, submit_scenario = self._generate_methods(
            properties_as_str
        )

        data = read_data_node(input_data_node)
        write_data_node(output_data_node, data)
        submit_sequence(sequence)
        submit_scenario(scenario)

    def _generate_configs(self, prefix: str, row_count: int, type_format: str, **kwargs):
        Config.unblock_update()
        tp.clean_all_entities_by_version(None)

        input_datanode_cfg = Config.configure_json_data_node(
            id=prefix + "_input_datanode",
            path=f"{self.input_folder_path}/input_{type_format}_{row_count}.json",
            **kwargs,
        )
        output_datanode_cfg = Config.configure_json_data_node(
            id=prefix + "_output_datanode",
            path=f"{self.output_folder_path}/output_{type_format}_{row_count}.json",
            **kwargs,
        )
        task_cfg = Config.configure_task(
            id=prefix + "_task", input=input_datanode_cfg, function=algorithm, output=output_datanode_cfg
        )
        pipeline_cfg = Config.configure_pipeline(id=prefix + "_pipeline", task_configs=[task_cfg])
        scenario_cfg = Config.configure_scenario(id=prefix + "_scenario", pipeline_configs=[pipeline_cfg])
        return scenario_cfg
