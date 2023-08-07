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

import mongomock
import taipy.core.taipy as tp
from taipy import Config
from taipy.core import Core
from taipy.core.config import JobConfig
from taipy.core.job.status import Status

from tests.utils import assert_true_after_time


def mult_by_2(a):
    return a


def build_skipped_jobs_config():
    input_config = Config.configure_data_node(id="input")
    intermediate_config = Config.configure_data_node(id="intermediate")
    output_config = Config.configure_data_node(id="output")
    task_config_1 = Config.configure_task("first", mult_by_2, input_config, intermediate_config, skippable=True)
    task_config_2 = Config.configure_task("second", mult_by_2, intermediate_config, output_config, skippable=True)
    pipeline_config = Config.configure_pipeline("pipeline", [task_config_1, task_config_2])
    return pipeline_config


class TestSkipJobs:
    @staticmethod
    def __test():
        pipeline_config = build_skipped_jobs_config()
        Core().run()
        pipeline = tp.create_pipeline(pipeline_config)
        pipeline.input.write(2)
        pipeline.submit()
        assert len(tp.get_jobs()) == 2
        for job in tp.get_jobs():
            assert_true_after_time(job.is_completed, msg=f"job {job.id} is not completed. Status: {job.status}")
        pipeline.submit()
        assert len(tp.get_jobs()) == 4
        skipped = []
        for job in tp.get_jobs():
            if job.status != Status.COMPLETED:
                assert_true_after_time(job.is_skipped, msg=f"job {job.id} is not skipped. Status: {job.status}")
                skipped.append(job)
        assert len(skipped) == 2

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
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
        Config.configure_global_app(repository_type="sql")
        self.__test()

    @mongomock.patch(servers=(("test_host", 27017),))
    def test_standalone_mongo_repo(self):
        Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)
        Config.configure_global_app(
            repository_type="mongo",
            repository_properties={"mongodb_hostname": "test_host", "application_db": "taipy"}
        )
        self.__test()
