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

import pandas as pd
import pytest
import taipy.core.taipy as tp
from taipy import Config
from taipy.core import Core
from taipy.core.config import JobConfig
from taipy.core.submission.submission_status import SubmissionStatus

from tests.test_example.algorithms import average
from .config import build_example_config
from tests.utils import assert_true_after_time


@pytest.mark.example_application
class TestExample:
    csv_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "dataset", "example_10.csv")
    excel_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "dataset", "example_10.xlsx")

    def test_development_fs_repo(self):
        self.__test()

    def test_development_sql_repo(self, init_sql_repo):
        self.__test()

    def test_standalone_fs_repo(self):
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
        self.__test(True)

    def test_standalone_sql_repo(self, init_sql_repo):
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
        self.__test(True)

    def __test(self, waiting_jobs_to_complete=False):
        with patch("sys.argv", ["prog"]):
            scenario_config = build_example_config(self.csv_path, self.excel_path)
            core = Core()
            core.run(force_restart=True)
            scenario = tp.create_scenario(scenario_config)
            submission = tp.submit(scenario)

            if waiting_jobs_to_complete:
                assert_true_after_time(
                    lambda: submission.submission_status == SubmissionStatus.COMPLETED,
                    time=120,
                    msg=lambda s: f"Submission status is {s.submission_status} after 30 seconds",
                    s=submission)
            else:
                assert submission.submission_status == SubmissionStatus.COMPLETED

            csv_sum_res = pd.read_csv(scenario.d5.path)
            excel_sum_res = pd.read_excel(scenario.d6.path)
            csv_out = pd.read_csv(scenario.d11.path)
            excel_out = pd.read_excel(scenario.d12.path)
            assert csv_sum_res.to_numpy().flatten().tolist() == [i * 20 for i in range(1, 11)]
            assert excel_sum_res.to_numpy().flatten().tolist() == [i * 2 for i in range(1, 11)]
            assert average(csv_sum_res["number"] - excel_sum_res["number"]) == csv_out.to_numpy()[0]
            assert average((csv_sum_res["number"] - excel_sum_res["number"]) * 10) == excel_out.to_numpy()[0]

            for path in [scenario.d5.path, scenario.d6.path, scenario.d11.path, scenario.d12.path]:
                os.remove(path)
            core.stop()
