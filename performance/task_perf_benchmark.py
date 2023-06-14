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
from taipy.core.task._task_manager_factory import _TaskManagerFactory

from perf_benchmark_abstract import PerfBenchmarkAbstract
from utils import algorithm, timer


class TaskPerfBenchmark(PerfBenchmarkAbstract):
    BENCHMARK_NAME = "Task perf"
    BENCHMARK_REPORT_FILE_NAME = "task_benchmark_report.csv"
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

        task_cfgs = self._generate_configs(repo_type)
        test_functions  = self._generate_methods(properties_as_str)

        create_task_multiple_times = test_functions[1]
        get_single_task_by_id = test_functions[2]
        get_all_tasks = test_functions[3]
        delete_task_by_id = test_functions[4]

        tasks = create_task_multiple_times(entity_count, task_cfgs)
        task = get_single_task_by_id(tasks[0].id)
        get_all_tasks()
        delete_task_by_id(task.id)

    @staticmethod
    def _generate_methods(properties_as_str):
        task_manager = _TaskManagerFactory._build_manager()

        @timer(properties_as_str)
        def create_task(task_configs):
            return task_manager._bulk_get_or_create(task_configs)

        @timer(properties_as_str)
        def create_task_multiple_times(entity_count: int, task_configs):
            tasks = []
            for _ in range(entity_count):
                tasks.append(task_manager._bulk_get_or_create(task_configs)[0])
            return tasks

        @timer(properties_as_str)
        def get_single_task_by_id(task_id):
            return tp.get(task_id)

        @timer(properties_as_str)
        def get_all_tasks():
            return tp.get_tasks()

        @timer(properties_as_str)
        def delete_task_by_id(task_id):
            tp.delete(task_id)

        return (create_task,
                create_task_multiple_times,
                get_single_task_by_id,
                get_all_tasks,
                delete_task_by_id)

    def _generate_configs(self, repo_type):
        Config.unblock_update()
        Config.configure_global_app(clean_entities_enabled=True, repository_type=repo_type)
        tp.clean_all_entities()

        input_datanode_cfgs = Config.configure_pickle_data_node(id="input_datanode")
        output_datanode_cfg = Config.configure_pickle_data_node(id="output_datanode")
        task_cfg = Config.configure_task(id="task", input=input_datanode_cfgs, function=algorithm, output=output_datanode_cfg)

        return [task_cfg]
