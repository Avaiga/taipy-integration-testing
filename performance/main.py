# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import taipy as tp

from csv_perf_benchmark import CSVPerfBenchmark
from end_to_end_scenario_creation_perf_benchmark import EndToEndScenarioCreationPerfBenchmark
from excel_perf_benchmark import ExcelPerfBenchmark
from json_perf_benchmark import JsonPerfBenchmark
from pickle_perf_benchmark import PicklePerfBenchmark
from scenario_perf_benchmark import ScenarioPerfBenchmark

# ROW_COUNTS = [10**3, 10**4]
ROW_COUNTS = [10**3]
ENTITY_COUNTS = [10**2]
SCENARIO_COUNTS = [10**1, 10**2]

if __name__ == "__main__":
    
    tp.run(tp.Core())
    
    # CSVPerfBenchmark(ROW_COUNTS).run()
    # ExcelPerfBenchmark(ROW_COUNTS).run()
    PicklePerfBenchmark(ROW_COUNTS).run()
    # JsonPerfBenchmark(ROW_COUNTS).run()
    # ScenarioPerfBenchmark(ENTITY_COUNTS).run()
    EndToEndScenarioCreationPerfBenchmark(SCENARIO_COUNTS).run()
