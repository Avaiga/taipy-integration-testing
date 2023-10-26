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

from unittest.mock import patch

import mongomock
import taipy.core.taipy as tp
from taipy import Config
from taipy.core import Core
from taipy.core.config import JobConfig

from tests.test_complex.utils.config_builders import build_churn_classification_config
from tests.utils import assert_true_after_time


class TestChurnClassification:
    @staticmethod
    def __test():
        scenario_cfg = build_churn_classification_config()
        with patch("sys.argv", ["prog"]):
            core = Core()
            core.run(force_restart=True)
        scenario = tp.create_scenario(scenario_cfg)
        jobs = tp.submit(scenario)
        for job in jobs:
            assert_true_after_time(
                job.is_completed, msg=f"job {job.id} is not completed. Status: {job.status}.", time=30
            )
        core.stop()

    def test_development_fs_repo(self):
        self.__test()

    def test_development_sql_repo(self, init_sql_repo):
        self.__test()

    @mongomock.patch(servers=(("test_host", 27017),))
    def test_development_mongo_repo(self):
        Config.configure_core(
            repository_type="mongo", repository_properties={"mongodb_hostname": "test_host", "application_db": "taipy"}
        )
        self.__test()

    def test_standalone_fs_repo(self):
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
        self.__test()

    def test_standalone_sql_repo(self, init_sql_repo):
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
        self.__test()

    @mongomock.patch(servers=(("test_host", 27017),))
    def test_standalone_mongo_repo(self):
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
        Config.configure_core(
            repository_type="mongo", repository_properties={"mongodb_hostname": "test_host", "application_db": "taipy"}
        )
        self.__test()
