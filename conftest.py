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
    from sqlalchemy.orm import close_all_sessions

    close_all_sessions()

    sleep(0.1)
    if os.path.exists(".data"):
        shutil.rmtree(".data", ignore_errors=True)
    if os.path.exists("test.db"):
        os.remove("test.db")

    init_managers()
    init_config()
    init_orchestrator()
    init_managers()
    init_config()


def init_config():
    from taipy import Config
    from taipy.core.config import (
        DataNodeConfig,
        JobConfig,
        PipelineConfig,
        ScenarioConfig,
        TaskConfig,
        _DataNodeConfigChecker,
        _JobConfigChecker,
        _PipelineConfigChecker,
        _ScenarioConfigChecker,
        _TaskConfigChecker,
        CoreSection,
    )
    from taipy.config import IssueCollector
    from taipy.config._config import _Config
    from taipy.config._serializer._toml_serializer import _TomlSerializer
    from taipy.config.checker._checker import _Checker
    from taipy.core.config import _inject_section

    Config.unblock_update()
    Config._default_config = _Config()._default_config()
    Config._python_config = _Config()
    Config._file_config = None
    Config._env_file_config = None
    Config._applied_config = _Config._default_config()
    Config._collector = IssueCollector()
    Config._serializer = _TomlSerializer()
    _Checker._checkers = []

    _inject_section(
        JobConfig, "job_config", JobConfig("development"), [("configure_job_executions", JobConfig._configure)], True
    )
    _inject_section(
        DataNodeConfig,
        "data_nodes",
        DataNodeConfig.default_config(),
        [
            ("configure_data_node", DataNodeConfig._configure),
            ("configure_default_data_node", DataNodeConfig._configure_default),
            ("configure_csv_data_node", DataNodeConfig._configure_csv),
            ("configure_json_data_node", DataNodeConfig._configure_json),
            ("configure_sql_table_data_node", DataNodeConfig._configure_sql_table),
            ("configure_sql_data_node", DataNodeConfig._configure_sql),
            ("configure_mongo_collection_data_node", DataNodeConfig._configure_mongo_collection),
            ("configure_in_memory_data_node", DataNodeConfig._configure_in_memory),
            ("configure_pickle_data_node", DataNodeConfig._configure_pickle),
            ("configure_excel_data_node", DataNodeConfig._configure_excel),
            ("configure_generic_data_node", DataNodeConfig._configure_generic),
        ],
    )
    _inject_section(
        TaskConfig,
        "tasks",
        TaskConfig.default_config(),
        [("configure_task", TaskConfig._configure), ("configure_default_task", TaskConfig._configure_default)],
    )
    _inject_section(
        PipelineConfig,
        "pipelines",
        PipelineConfig.default_config(),
        [
            ("configure_pipeline", PipelineConfig._configure),
            ("configure_default_pipeline", PipelineConfig._configure_default),
        ],
    )
    _inject_section(
        ScenarioConfig,
        "scenarios",
        ScenarioConfig.default_config(),
        [
            ("configure_scenario", ScenarioConfig._configure),
            ("configure_default_scenario", ScenarioConfig._configure_default),
            ("configure_scenario_from_tasks", ScenarioConfig._configure_from_tasks),
        ],
    )
    _inject_section(
        CoreSection,
        "core",
        CoreSection.default_config(),
        [("configure_core", CoreSection._configure)],
        add_to_unconflicted_sections=True,
    )
    _Checker.add_checker(_JobConfigChecker)
    _Checker.add_checker(_DataNodeConfigChecker)
    _Checker.add_checker(_TaskConfigChecker)
    _Checker.add_checker(_PipelineConfigChecker)
    _Checker.add_checker(_ScenarioConfigChecker)


def init_managers():
    from taipy.core.cycle._cycle_manager_factory import _CycleManagerFactory
    from taipy.core.data._data_manager_factory import _DataManagerFactory
    from taipy.core.job._job_manager_factory import _JobManagerFactory
    from taipy.core.pipeline._pipeline_manager_factory import _PipelineManagerFactory
    from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
    from taipy.core.task._task_manager_factory import _TaskManagerFactory
    from taipy.core._version._version_manager_factory import _VersionManagerFactory

    _CycleManagerFactory._build_manager()._delete_all()
    _ScenarioManagerFactory._build_manager()._delete_all()
    _PipelineManagerFactory._build_manager()._delete_all()
    _JobManagerFactory._build_manager()._delete_all()
    _TaskManagerFactory._build_manager()._delete_all()
    _DataManagerFactory._build_manager()._delete_all()
    _VersionManagerFactory._build_manager()._delete_all()


def init_orchestrator():
    from queue import Queue

    from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory

    if _OrchestratorFactory._orchestrator is None:
        _OrchestratorFactory._build_orchestrator()
    _OrchestratorFactory._build_dispatcher(force_restart=True)
    _OrchestratorFactory._orchestrator.jobs_to_run = Queue()
    _OrchestratorFactory._orchestrator.blocked_jobs = []
