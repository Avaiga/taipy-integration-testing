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
import sys
from datetime import datetime

import taipy as tp
from taipy import Config
from taipy.core.data._data_manager_factory import _DataManagerFactory

from perf_benchmark_abstract import PerfBenchmarkAbstract
from utils import algorithm, timer


class DataNodePerfBenchmark(PerfBenchmarkAbstract):
    BENCHMARK_NAME = "DataNode perf"
    BENCHMARK_REPORT_FILE_NAME = "data_node_benchmark_report.csv"
    HEADERS = ['github_sha', 'datetime', 'entity_counts', 'function_name', 'time_elapsed']
    DEFAULT_ENTITY_COUNTS = [10**2, 10**3, 10**4]


    def __init__(self, github_sha: str, entity_counts: list[int] = None, report_path: str = None):
        super().__init__(report_path=report_path)
        self.github_sha = github_sha if github_sha else 'None'
        self.entity_counts = entity_counts if entity_counts else self.DEFAULT_ENTITY_COUNTS.copy()

    def run(self):
        self.log_header()
        with open(self.report_path, "a", encoding="utf-8") as f:
            sys.stdout = f
            if os.path.getsize(self.report_path) == 0:
                print(','.join(self.HEADERS))
            time_start = str(datetime.today())
            for test_parameters in self._generate_test_parameter_list():
                self._run_test(test_parameters, time_start)

    def _generate_test_parameter_list(self) -> list:
        test_parameter_list = []
        for entity_count in self.entity_counts:
            test_parameter_list.append([entity_count])
        return test_parameter_list

    def _run_test(self, test_parameters: dict, time_start):
        entity_count = test_parameters[0]

        properties_as_str = [self.github_sha, time_start, str(entity_count)]

        data_node_cfgs = self._generate_configs()
        _, create_data_multiple_times = self._generate_methods(properties_as_str)
        create_data_multiple_times(entity_count, data_node_cfgs)

    @staticmethod
    def _generate_methods(properties_as_str):
        data_node_manager = _DataManagerFactory._build_manager()
        
        @timer(properties_as_str)
        def create_data_node(data_node_configs):
            return data_node_manager._bulk_get_or_create(data_node_configs)

        @timer(properties_as_str)
        def create_data_node_multiple_times(entity_count: int, data_node_configs):
            data_nodes = []
            for _ in range(entity_count):
                data_nodes.append(data_node_manager._bulk_get_or_create(data_node_configs))
            return data_nodes

        return create_data_node, create_data_node_multiple_times

    def _generate_configs(self):
        Config.unblock_update()
        Config.configure_global_app(clean_entities_enabled=True)
        tp.clean_all_entities()

        datanode_cfg = Config.configure_pickle_data_node(id="datanode")

        return [datanode_cfg]
