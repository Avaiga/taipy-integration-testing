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

from unittest.mock import patch

import pytest
import taipy.core.taipy as tp
from taipy import Config
from taipy.core import Core
from taipy.core.config import JobConfig

from tests.test_skipped_jobs.config import build_skipped_jobs_config
from tests.utils import assert_true_after_time



class TestSkipJobs:

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

    @staticmethod
    def __test(waiting_for_completion=False):
        with patch("sys.argv", ["prog"]):
            scenario_config = build_skipped_jobs_config()
            core = Core()
            core.run()
            scenario = tp.create_scenario(scenario_config)

            submission_one = scenario.submit()
            assert len(tp.get_jobs()) == 2
            if waiting_for_completion:
                assert_true_after_time(lambda: all(job.is_completed() for job in submission_one.jobs))
            else:
                assert all(job.is_completed() for job in tp.get_jobs())

            submission_two = scenario.submit()
            assert len(tp.get_jobs()) == 4
            if waiting_for_completion:
                assert_true_after_time(lambda: all(job.is_skipped() for job in submission_two.jobs))
            else:
                assert all(job.is_skipped() for job in submission_two.jobs)

            core.stop()
