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
from perf_benchmark_abstract import PerfBenchmarkAbstract
from taipy import Config
from utils import algorithm, timer


class PipelinePerfBenchmark(PerfBenchmarkAbstract):
    BENCHMARK_NAME = "Pipeline perf"
    BENCHMARK_REPORT_FILE_NAME = "pipeline_benchmark_report.csv"
    HEADERS = ["github_sha", "datetime", "repo_type", "entity_counts", "function_name", "time_elapsed"]
    DEFAULT_ENTITY_COUNTS = [10**2, 10**3, 10**4]
    REPO_CONFIGS = [
        {"repository_type": "default"},
        {"repository_type": "sql"},
        {"repository_type": "mongo", "repository_properties": {"mongo_username": "taipy", "mongo_password": "taipy"}},
    ]

    def __init__(self, github_sha: str, entity_counts: list[int] = None, report_path: str = None):
        super().__init__(report_path=report_path)
        self.github_sha = github_sha
        self.entity_counts = entity_counts if entity_counts else self.DEFAULT_ENTITY_COUNTS.copy()

    def run(self):
        self.log_header()
        with open(self.report_path, "a", encoding="utf-8") as f:
            sys.stdout = f
            if os.path.getsize(self.report_path) == 0:
                print(",".join(self.HEADERS))
            time_start = str(datetime.today())
            for test_parameters in self._generate_test_parameter_list():
                self._run_test(test_parameters, time_start)
                self.clean_test_state()

    def _generate_test_parameter_list(self) -> list:
        test_parameter_list = []
        for repo_config in self.REPO_CONFIGS:
            for entity_count in self.entity_counts:
                test_parameter_list.append([repo_config, entity_count])
        return test_parameter_list

    def _run_test(self, test_parameters: dict, time_start):
        repo_config, entity_count = test_parameters

        properties_as_str = [self.github_sha, time_start, repo_config.get("repository_type"), str(entity_count)]

        pipeline_cfg = self._generate_configs(repo_config)
        test_functions = self._generate_methods(properties_as_str)

        create_pipeline_multiple_times = test_functions[1]
        get_single_pipeline_by_id = test_functions[2]
        get_all_pipelines = test_functions[3]
        delete_pipeline_by_id = test_functions[4]

        pipelines = create_pipeline_multiple_times(entity_count, pipeline_cfg)
        pipeline = get_single_pipeline_by_id(pipelines[0].id)
        get_all_pipelines()
        delete_pipeline_by_id(pipeline.id)

    @staticmethod
    def _generate_methods(properties_as_str):
        @timer(properties_as_str)
        def create_pipeline(pipeline_config):
            return tp.create_pipeline(pipeline_config)

        @timer(properties_as_str)
        def create_pipeline_multiple_times(entity_count: int, pipeline_config):
            pipelines = []
            for _ in range(entity_count):
                pipelines.append(tp.create_pipeline(pipeline_config))
            return pipelines

        @timer(properties_as_str)
        def get_single_pipeline_by_id(pipeline_id):
            return tp.get(pipeline_id)

        @timer(properties_as_str)
        def get_all_pipelines():
            return tp.get_pipelines()

        @timer(properties_as_str)
        def delete_pipeline_by_id(pipeline_id):
            tp.delete(pipeline_id)

        return (
            create_pipeline,
            create_pipeline_multiple_times,
            get_single_pipeline_by_id,
            get_all_pipelines,
            delete_pipeline_by_id,
        )

    def _generate_configs(self, repo_config):
        Config.unblock_update()
        Config.configure_core(**repo_config)
        tp.clean_all_entities_by_version(None)

        input_datanode_cfgs = Config.configure_pickle_data_node(id="input_datanode")
        output_datanode_cfg = Config.configure_pickle_data_node(id="output_datanode")
        task_cfg = Config.configure_task(
            id="task", input=input_datanode_cfgs, function=algorithm, output=output_datanode_cfg
        )
        pipeline_cfg = Config.configure_pipeline(id="pipeline", task_configs=task_cfg)

        return pipeline_cfg
