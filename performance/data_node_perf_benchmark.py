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
    HEADERS = ['github_sha', 'datetime', 'repo_type', 'entity_counts', 'function_name', 'time_elapsed']
    DEFAULT_ENTITY_COUNTS = [10**2, 10**3, 10**4]
    REPO_TYPES = ['default', 'sql', 'mongo']


    def __init__(self, github_sha: str, entity_counts: list[int] = None, report_path: str = None):
        super().__init__(report_path=report_path)
        self.github_sha = github_sha
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
                self.clean_test_state()

    def _generate_test_parameter_list(self) -> list:
        test_parameter_list = []
        for repo_type in self.REPO_TYPES:
            for entity_count in self.entity_counts:
                test_parameter_list.append([repo_type, entity_count])
        return test_parameter_list

    def _run_test(self, test_parameters: dict, time_start):
        repo_type, entity_count = test_parameters

        properties_as_str = [self.github_sha, time_start, repo_type, str(entity_count)]

        data_node_cfgs = self._generate_configs(repo_type)
        test_functions = self._generate_methods(properties_as_str)

        create_data_multiple_times = test_functions[1]
        get_single_data_node_by_id = test_functions[2]
        get_all_data_nodes = test_functions[3]
        delete_data_node_by_id = test_functions[4]

        data_nodes = create_data_multiple_times(entity_count, data_node_cfgs)
        data_node = get_single_data_node_by_id(data_nodes[0].id)
        get_all_data_nodes()
        delete_data_node_by_id(data_node.id)

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
                data_nodes.append(data_node_manager._bulk_get_or_create(data_node_configs)[data_node_configs[0]])
            return data_nodes

        @timer(properties_as_str)
        def get_single_data_node_by_id(data_node_id):
            return tp.get(data_node_id)

        @timer(properties_as_str)
        def get_all_data_nodes():
            return tp.get_tasks()

        @timer(properties_as_str)
        def delete_data_node_by_id(data_node_id):
            tp.delete(data_node_id)

        return (create_data_node,
                create_data_node_multiple_times,
                get_single_data_node_by_id,
                get_all_data_nodes,
                delete_data_node_by_id)

    def _generate_configs(self, repo_type):
        Config.unblock_update()
        Config.configure_global_app(clean_entities_enabled=True, repository_type=repo_type)
        tp.clean_all_entities()

        datanode_cfg = Config.configure_pickle_data_node(id="datanode")

        return [datanode_cfg]
