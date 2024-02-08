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

import taipy.core.taipy as tp
from taipy import Config
from taipy.core import Core
from taipy.core.config import JobConfig
from taipy.core.submission.submission_status import SubmissionStatus

from tests.utils import assert_true_after_time

from .config import build_churn_config
from .. import utils


class TestChurnClassification:
    data_set_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "dataset", "churn_10000.csv")

    def test_development_fs_repo(self):
        self.waiting_jobs_to_complete = False
        self.__run()

    def test_development_sql_repo(self, init_sql_repo):
        self.waiting_jobs_to_complete = False
        self.__run()

    def test_standalone_fs_repo(self):
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=4)
        self.waiting_jobs_to_complete = True
        self.__run()

    def test_standalone_sql_repo(self, init_sql_repo):
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=4)
        self.waiting_jobs_to_complete = True
        self.__run()

    def __run(self):
        with patch("sys.argv", ["prog"]):
            scenario_cfg = build_churn_config(self.data_set_path)
            core = Core()
            core.run(force_restart=True)
            scenario = tp.create_scenario(scenario_cfg)
            for inpt in scenario.get_inputs():
                # Checking this allows not to submit scenario if it is blocked by some input not being ready
                assert inpt.is_ready_for_reading
            submission = tp.submit(scenario)
            if self.waiting_jobs_to_complete:
                # 12 jobs must be processed to complete the scenario. It may take some time.
                assert_true_after_time(
                    lambda: submission.submission_status == SubmissionStatus.COMPLETED,
                    time=300,
                    msg=lambda s: utils.message(s, 300),
                    s=submission,
                )
            else:
                assert submission.submission_status == SubmissionStatus.COMPLETED
            core.stop()
