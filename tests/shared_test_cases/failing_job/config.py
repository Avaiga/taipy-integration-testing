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

from datetime import datetime

from taipy import Frequency, Scope
from taipy.config.config import Config

from .algorithms import failing_job, predict

historical_data_set = Config.configure_csv_data_node(
    id="historical_data_set", path="tests//shared_test_cases/arima/daily-min-temperatures.csv", scope=Scope.GLOBAL
)

arima_model = Config.configure_data_node(id="arima_model")

dates_to_forecast = Config.configure_data_node(
    id="dates_to_forecast", scope=Scope.SCENARIO, default_data=[datetime(1991, 1, 1).isoformat()]
)

forecast_values = Config.configure_excel_data_node(
    id="forecast_values", has_header=False, path="tests//shared_test_cases/arima/res.xlsx"
)

arima_fail_algo = Config.configure_task(
    id="arima_training", input=historical_data_set, function=failing_job, output=arima_model
)

arima_scoring_algo = Config.configure_task(
    id="arima_scoring", input=[arima_model, dates_to_forecast], function=predict, output=forecast_values
)

arima_pipeline = Config.configure_pipeline(id="arima_pipelines", task_configs=[arima_fail_algo, arima_scoring_algo])

arima_scenario_config = Config.configure_scenario(
    id="Arima_scenario", pipeline_configs=[arima_pipeline], frequency=Frequency.DAILY
)
