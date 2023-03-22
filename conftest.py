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
import shutil

import pytest


@pytest.fixture(autouse=True)
def cleanup_data():
    from time import sleep

    sleep(0.1)
    if os.path.exists(".data"):
        shutil.rmtree(".data", ignore_errors=True)
    if os.path.exists("test.db"):
        os.remove("test.db")

    init_orchestrator()
    init_managers()
    init_config()


def init_config():
    from taipy import Config
    from taipy.config import IssueCollector
    from taipy.config._config import _Config
    from taipy.config._serializer._toml_serializer import _TomlSerializer

    Config.unblock_update()
    Config._default_config = _Config()._default_config()
    Config._python_config = _Config()
    Config._file_config = None
    Config._env_file_config = None
    Config._applied_config = _Config._default_config()
    Config._collector = IssueCollector()
    Config._serializer = _TomlSerializer()


def init_managers():
    from taipy.core.cycle._cycle_manager import _CycleManager
    from taipy.core.data._data_manager import _DataManager
    from taipy.core.job._job_manager import _JobManager
    from taipy.core.pipeline._pipeline_manager import _PipelineManager
    from taipy.core.scenario._scenario_manager import _ScenarioManager
    from taipy.core.task._task_manager import _TaskManager

    _ScenarioManager._delete_all()
    _PipelineManager._delete_all()
    _DataManager._delete_all()
    _TaskManager._delete_all()
    _JobManager._delete_all()
    _CycleManager._delete_all()


def init_orchestrator():
    from queue import Queue

    from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory

    if _OrchestratorFactory._orchestrator is None:
        _OrchestratorFactory._build_orchestrator()
    _OrchestratorFactory._build_dispatcher()
    _OrchestratorFactory._orchestrator.jobs_to_run = Queue()
    _OrchestratorFactory._orchestrator.blocked_jobs = []
