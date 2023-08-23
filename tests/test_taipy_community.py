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

import taipy as tp
from tests.shared_test_cases.arima.config import build_arima_config


def test_submit_scenario_submit_success():
    arima_scenario_config = build_arima_config()
    scenario = tp.create_scenario(arima_scenario_config)
    tp.submit(scenario)

    assert scenario.forecast_values.read() is not None
    assert len(tp.get_tasks()) == 2
    assert len(tp.get_jobs()) == 2
    assert len(tp.get_data_nodes()) == 4
