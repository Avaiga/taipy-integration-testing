# Copyright 2024 Avaiga Private Limited
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
import pathlib
from unittest.mock import patch

import taipy as tp
from taipy import Config, Core
from taipy.core.config import JobConfig
from taipy.core.submission.submission_status import SubmissionStatus

from .config import build_arima_config
from tests.utils import assert_true_after_time


class TestDailyTemperature:
    CSV_INPUT_PATH = os.path.join(pathlib.Path(__file__).parent.resolve(), "dataset", "daily-min-temperatures.csv")
    XLSX_OUTPUT_PATH = os.path.join(pathlib.Path(__file__).parent.resolve(), "../outputs", "output.xlsx")

    def test_development_fs_repo(self):
        self.__run()

    def test_development_sql_repo(self, init_sql_repo):
        self.__run()

    def test_standalone_fs_repo(self):
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
        self.__run(True)

    def test_standalone_sql_repo(self, init_sql_repo):
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
        self.__run(True)

    def __run(self, waiting_jobs_to_complete=False):
        with patch("sys.argv", ["prog"]):
            arima_scenario_config = build_arima_config(self.CSV_INPUT_PATH, self.XLSX_OUTPUT_PATH)
            core = Core()
            core.run()
            scenario = tp.create_scenario(arima_scenario_config)
            submission = tp.submit(scenario)

            if waiting_jobs_to_complete:
                assert_true_after_time(lambda: submission.submission_status == SubmissionStatus.COMPLETED)
            else:
                assert submission.submission_status == SubmissionStatus.COMPLETED
            assert scenario.forecast_values.read() is not None
            assert len(tp.get_tasks()) == 2
            assert len(tp.get_jobs()) == 2
            assert len(tp.get_data_nodes()) == 4

            core.stop()
