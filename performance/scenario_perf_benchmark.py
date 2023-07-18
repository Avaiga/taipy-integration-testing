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
from taipy.config.common.scope import Scope
from utils import algorithm, timer


class ScenarioPerfBenchmark(PerfBenchmarkAbstract):
    BENCHMARK_NAME = "Scenario perf"
    BENCHMARK_REPORT_FILE_NAME = "scenario_benchmark_report.csv"
    HEADERS = [
        "github_sha",
        "datetime",
        "repo_type",
        "entity_counts",
        "multi_entity_type",
        "scope",
        "function_name",
        "time_elapsed",
    ]
    DEFAULT_ENTITY_COUNTS = [10**2, 10**3, 10**4]
    REPO_CONFIGS = [
        {"repository_type": "default"},
        {"repository_type": "sql"},
        {"repository_type": "mongo", "repository_properties": {"mongo_username": "taipy", "mongo_password": "taipy"}},
    ]
    MULTI_ENTITY_TYPES = ["datanode", "task", "pipeline", "scenario"]
    DATA_NODE_SCOPES = [Scope.PIPELINE, Scope.SCENARIO, Scope.CYCLE, Scope.GLOBAL]

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
                for multi_entity_type in self.MULTI_ENTITY_TYPES:
                    for data_node_scope in self.DATA_NODE_SCOPES:
                        test_parameter_list.append((repo_config, entity_count, multi_entity_type, data_node_scope))
        return test_parameter_list

    def _run_test(self, test_parameters: dict, time_start):
        repo_config, entity_count, multi_entity_type, data_node_scope = test_parameters

        properties_as_str = [
            self.github_sha,
            time_start,
            repo_config.get("repository_type"),
            str(entity_count),
            str(multi_entity_type),
            str(data_node_scope),
        ]

        scenario_cfg = self._generate_configs(repo_config, entity_count, multi_entity_type, data_node_scope)
        test_functions = self._generate_methods(properties_as_str)

        create_scenario = test_functions[0]
        create_scenario_multiple_times = test_functions[1]
        get_single_scenario_by_id = test_functions[2]
        get_all_scenarios = test_functions[3]
        delete_scenario_by_id = test_functions[4]

        if multi_entity_type == "scenario":
            scenarios = create_scenario_multiple_times(entity_count, scenario_cfg)
            scenario = get_single_scenario_by_id(scenarios[0].id)
            get_all_scenarios()
            delete_scenario_by_id(scenario.id)
        else:
            create_scenario(scenario_cfg)

    @staticmethod
    def _generate_methods(properties_as_str):
        @timer(properties_as_str)
        def create_scenario(scenario_config):
            return tp.create_scenario(scenario_config)

        @timer(properties_as_str)
        def create_scenario_multiple_times(entity_count: int, scenario_config):
            scenarios = []
            for _ in range(entity_count):
                scenarios.append(tp.create_scenario(scenario_config))
            return scenarios

        @timer(properties_as_str)
        def get_single_scenario_by_id(scenario_id):
            return tp.get(scenario_id)

        @timer(properties_as_str)
        def get_all_scenarios():
            return tp.get_scenarios()

        @timer(properties_as_str)
        def delete_scenario_by_id(scenario_id):
            tp.delete(scenario_id)

        return (
            create_scenario,
            create_scenario_multiple_times,
            get_single_scenario_by_id,
            get_all_scenarios,
            delete_scenario_by_id,
        )

    def _generate_configs(
        self, repo_config, entity_count, multi_entity_type: str = "datanode", data_node_scope: Scope = Scope.PIPELINE
    ):
        Config.unblock_update()
        Config.configure_core(**repo_config)
        tp.clean_all_entities_by_version(None)

        nb_dn = entity_count if multi_entity_type == "datanode" else 1
        nb_task = entity_count if multi_entity_type == "task" else 1
        nb_pipeline = entity_count if multi_entity_type == "pipeline" else 1

        input_datanode_cfgs = []
        task_cfgs = []
        pipeline_cfgs = []

        for i in range(nb_dn):
            input_datanode_cfgs.append(
                Config.configure_pickle_data_node(id=f"input_datanode_{i}", scope=data_node_scope)
            )

        output_datanode_cfg = [Config.configure_pickle_data_node(id="output_datanode", scope=data_node_scope)]

        for i in range(nb_task):
            task_cfgs.append(
                Config.configure_task(
                    id=f"task_{i}", input=input_datanode_cfgs, function=algorithm, output=output_datanode_cfg
                )
            )

        for i in range(nb_pipeline):
            pipeline_cfgs.append(Config.configure_pipeline(id=f"pipeline_{i}", task_configs=task_cfgs))

        scenario_cfg = Config.configure_scenario(id="scenario", pipeline_configs=pipeline_cfgs)

        return scenario_cfg
