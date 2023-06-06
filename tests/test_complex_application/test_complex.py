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
import os

import mongomock
import pandas as pd
import taipy.core.taipy as tp
from taipy import Config
from taipy.core import Core
from taipy.core.config import JobConfig

from tests.test_complex_application.utils.algos import average
from tests.test_complex_application.utils.config_builders import build_complex_required_file_paths, build_complex_config
from tests.utils import assert_true_after_time


class TestComplexApp:

    @staticmethod
    def __test():
        _, _, csv_path_sum, excel_path_sum, excel_path_out, csv_path_out = build_complex_required_file_paths()
        scenario_config = build_complex_config()
        Core().run(force_restart=True)
        scenario = tp.create_scenario(scenario_config)
        jobs = tp.submit(scenario)
        for job in jobs:
            assert_true_after_time(job.is_completed, msg=f"job {job.id} is not completed. Status: {job.status}.")

        csv_sum_res = pd.read_csv(csv_path_sum)
        excel_sum_res = pd.read_excel(excel_path_sum)
        csv_out = pd.read_csv(csv_path_out)
        excel_out = pd.read_excel(excel_path_out)
        assert csv_sum_res.to_numpy().flatten().tolist() == [i * 20 for i in range(1, 11)]
        assert excel_sum_res.to_numpy().flatten().tolist() == [i * 2 for i in range(1, 11)]
        assert average(csv_sum_res["number"] - excel_sum_res["number"]) == csv_out.to_numpy()[0]
        assert average((csv_sum_res["number"] - excel_sum_res["number"]) * 10) == excel_out.to_numpy()[0]

        for path in [csv_path_sum, excel_path_sum, csv_path_out, excel_path_out]:
            os.remove(path)

    def test_development_fs_repo(self):
        self.__test()

    def test_development_sql_repo(self):
        Config.configure_global_app(repository_type="sql")
        self.__test()

    @mongomock.patch(servers=(("test_host", 27017),))
    def test_development_mongo_repo(self):
        Config.configure_global_app(
            repository_type="mongo",
            repository_properties={"mongodb_hostname": "test_host", "application_db": "taipy"}
        )
        self.__test()

    def test_standalone_fs_repo(self):
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
        self.__test()

    def test_standalone_sql_repo(self):
        Config.configure_global_app(repository_type="sql")
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
        self.__test()

    @mongomock.patch(servers=(("test_host", 27017),))
    def test_standalone_mongo_repo(self):
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
        Config.configure_global_app(
            repository_type="mongo",
            repository_properties={"mongodb_hostname": "test_host", "application_db": "taipy"}
        )
        self.__test()
