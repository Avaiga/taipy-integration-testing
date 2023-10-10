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

import argparse

import taipy as tp
from csv_perf_benchmark import CSVPerfBenchmark
from data_node_perf_benchmark import DataNodePerfBenchmark
from end_to_end_scenario_creation_perf_benchmark import EndToEndScenarioCreationPerfBenchmark
from excel_perf_benchmark import ExcelPerfBenchmark
from json_perf_benchmark import JsonPerfBenchmark
from pickle_perf_benchmark import PicklePerfBenchmark
from scenario_perf_benchmark import ScenarioPerfBenchmark
from sequence_perf_benchmark import SequencePerfBenchmark
from task_perf_benchmark import TaskPerfBenchmark

ROW_COUNTS = [10**2, 10**3]
ENTITY_COUNTS = [10**1, 10**2]
SCENARIO_COUNTS = [10**1, 10**2]
DATANODE_PERF_BENCHMARKS = [CSVPerfBenchmark, ExcelPerfBenchmark, PicklePerfBenchmark, JsonPerfBenchmark]
ENTITY_PERF_BENCHMARKS = [DataNodePerfBenchmark, TaskPerfBenchmark, ScenarioPerfBenchmark]
# ENTITY_PERF_BENCHMARKS = [DataNodePerfBenchmark, TaskPerfBenchmark, SequencePerfBenchmark, ScenarioPerfBenchmark]

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--github-sha", help="The SHA value of the commit that triggered this action", default="")
    parser.add_argument("--repo", help="The Taipy repo that called this action", default="taipy-core")
    args = parser.parse_args()

    for datanode_perf_benchmark in DATANODE_PERF_BENCHMARKS:
        datanode_perf_benchmark(args.github_sha, ROW_COUNTS).run()

    for entity_perf_benchmark in ENTITY_PERF_BENCHMARKS:
        entity_perf_benchmark(args.github_sha, ENTITY_COUNTS).run()

    # EndToEndScenarioCreationPerfBenchmark(SCENARIO_COUNTS).run()
