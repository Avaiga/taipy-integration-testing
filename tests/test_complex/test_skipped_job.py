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

from time import sleep
from unittest.mock import patch

import pytest
import taipy.core.taipy as tp
from taipy import Config
from taipy.core import Core
from taipy.core.config import JobConfig
from taipy.core.job.status import Status

from tests.utils import assert_true_after_time


def mult_by_2(a):
    return a


def build_skipped_jobs_config():
    input_config = Config.configure_data_node(id="input_dn")
    intermediate_config = Config.configure_data_node(id="intermediate_dn")
    output_config = Config.configure_data_node(id="output_dn")
    task_config_1 = Config.configure_task("first", mult_by_2, input_config, intermediate_config, skippable=True)
    task_config_2 = Config.configure_task("second", mult_by_2, intermediate_config, output_config, skippable=True)
    scenario_config = Config.configure_scenario("scenario", task_configs=[task_config_1, task_config_2])
    return scenario_config


@pytest.mark.skipped
class TestSkipJobs:
    @staticmethod
    def __test():
        scenario_config = build_skipped_jobs_config()
        with patch("sys.argv", ["prog"]):
            core = Core()
            core.run()
        scenario = tp.create_scenario(scenario_config)
        scenario.input_dn.write(2)
        scenario.submit()
        assert len(tp.get_jobs()) == 2
        sleep(10)
        assert_true_after_time(
            lambda: all(job.is_completed() for job in tp.get_jobs()),
        )
        scenario.submit()
        assert len(tp.get_jobs()) == 4
        sleep(10)
        assert_true_after_time(
            lambda: all(job.is_skipped() or job.is_completed() for job in tp.get_jobs()),
        )
        skipped = []
        for job in tp.get_jobs():
            if job.status != Status.COMPLETED:
                if job.is_skipped():
                    skipped.append(job)
                else:
                    print(f"job {job.id} is not skipped. Status: {job.status}")
        assert len(skipped) == 2

        core.stop()

    def test_development_fs_repo(self):
        self.__test()

    def test_development_sql_repo(self, tmp_sqlite):
        Config.configure_global_app(repository_type="sql", repository_properties={"db_location": tmp_sqlite})
        self.__test()

    def test_standalone_fs_repo(self):
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
        self.__test()

    def test_standalone_sql_repo(self, tmp_sqlite):
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
        Config.configure_global_app(repository_type="sql", repository_properties={"db_location": tmp_sqlite})
        self.__test()
