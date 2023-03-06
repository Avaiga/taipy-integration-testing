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
from end_to_end_scenario_creation_perf_benchmark import EndToEndScenarioCreationPerfBenchmark
from excel_perf_benchmark import ExcelPerfBenchmark
from json_perf_benchmark import JsonPerfBenchmark
from pickle_perf_benchmark import PicklePerfBenchmark
from scenario_perf_benchmark import ScenarioPerfBenchmark
from pipeline_perf_benchmark import PipelinePerfBenchmark
from task_perf_benchmark import TaskPerfBenchmark
from data_node_perf_benchmark import DataNodePerfBenchmark

# ROW_COUNTS = [10**3, 10**4]
ROW_COUNTS = [10**3]
ENTITY_COUNTS = [10**2]
SCENARIO_COUNTS = [10**1, 10**2]

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--github-sha', help='The SHA value of the commit that triggered this action', default=None)
    parser.add_argument('--repo', help='The Taipy repo that called this action', default='taipy-core')
    args = parser.parse_args()

    tp.run(tp.Core())
    CSVPerfBenchmark(args.github_sha, ROW_COUNTS).run()
    ExcelPerfBenchmark(args.github_sha, ROW_COUNTS).run()
    PicklePerfBenchmark(args.github_sha, ROW_COUNTS).run()
    JsonPerfBenchmark(args.github_sha, ROW_COUNTS).run()
    DataNodePerfBenchmark(args.github_sha, ENTITY_COUNTS).run()
    TaskPerfBenchmark(args.github_sha, ENTITY_COUNTS).run()
    PipelinePerfBenchmark(args.github_sha, ENTITY_COUNTS).run()
    ScenarioPerfBenchmark(args.github_sha, ENTITY_COUNTS).run()
    # EndToEndScenarioCreationPerfBenchmark(SCENARIO_COUNTS).run()
