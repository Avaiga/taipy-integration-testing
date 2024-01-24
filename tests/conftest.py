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
import shutil
from queue import Queue

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import close_all_sessions
from taipy.config import _inject_section
from taipy.config._config import _Config
from taipy.config._config_comparator._config_comparator import _ConfigComparator
from taipy.config._serializer._toml_serializer import _TomlSerializer
from taipy.config.checker._checker import _Checker
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.config import Config
from taipy.core._core import Core
from taipy.core._orchestrator._orchestrator_factory import _OrchestratorFactory
from taipy.core._repository.db._sql_connection import _SQLConnection
from taipy.core._version._version_manager_factory import _VersionManagerFactory
from taipy.core.config import (
    CoreSection,
    DataNodeConfig,
    JobConfig,
    MigrationConfig,
    ScenarioConfig,
    TaskConfig,
    _ConfigIdChecker,
    _CoreSectionChecker,
    _DataNodeConfigChecker,
    _JobConfigChecker,
    _ScenarioConfigChecker,
    _TaskConfigChecker,
)
from taipy.core.cycle._cycle_manager_factory import _CycleManagerFactory
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.job._job_manager_factory import _JobManagerFactory
from taipy.core.notification.notifier import Notifier
from taipy.core.scenario._scenario_manager_factory import _ScenarioManagerFactory
from taipy.core.sequence._sequence_manager_factory import _SequenceManagerFactory
from taipy.core.submission._submission_manager_factory import _SubmissionManagerFactory
from taipy.core.task._task_manager_factory import _TaskManagerFactory


@pytest.fixture
def reset_configuration_singleton():
    def _reset_configuration_singleton():
        Config.unblock_update()

        Config._default_config = _Config()._default_config()
        Config._python_config = _Config()
        Config._file_config = _Config()
        Config._env_file_config = _Config()
        Config._applied_config = _Config()
        Config._collector = IssueCollector()
        Config._serializer = _TomlSerializer()
        Config._comparator = _ConfigComparator()
        _Checker._checkers = []

    return _reset_configuration_singleton


@pytest.fixture
def inject_core_sections():
    def _inject_core_sections():
        _inject_section(
            JobConfig,
            "job_config",
            JobConfig("development"),
            [("configure_job_executions", JobConfig._configure)],
            True,
        )
        _inject_section(
            CoreSection,
            "core",
            CoreSection.default_config(),
            [("configure_core", CoreSection._configure)],
            add_to_unconflicted_sections=True,
        )
        _inject_section(
            DataNodeConfig,
            "data_nodes",
            DataNodeConfig.default_config(),
            [
                ("configure_data_node", DataNodeConfig._configure),
                ("configure_data_node_from", DataNodeConfig._configure_from),
                ("set_default_data_node_configuration", DataNodeConfig._set_default_configuration),
                ("configure_csv_data_node", DataNodeConfig._configure_csv),
                ("configure_json_data_node", DataNodeConfig._configure_json),
                ("configure_sql_table_data_node", DataNodeConfig._configure_sql_table),
                ("configure_sql_data_node", DataNodeConfig._configure_sql),
                ("configure_mongo_collection_data_node", DataNodeConfig._configure_mongo_collection),
                ("configure_in_memory_data_node", DataNodeConfig._configure_in_memory),
                ("configure_pickle_data_node", DataNodeConfig._configure_pickle),
                ("configure_excel_data_node", DataNodeConfig._configure_excel),
                ("configure_generic_data_node", DataNodeConfig._configure_generic),
                ("configure_s3_object_data_node", DataNodeConfig._configure_s3_object),
            ],
        )
        _inject_section(
            TaskConfig,
            "tasks",
            TaskConfig.default_config(),
            [
                ("configure_task", TaskConfig._configure),
                ("set_default_task_configuration", TaskConfig._set_default_configuration),
            ],
        )
        _inject_section(
            ScenarioConfig,
            "scenarios",
            ScenarioConfig.default_config(),
            [
                ("configure_scenario", ScenarioConfig._configure),
                ("set_default_scenario_configuration", ScenarioConfig._set_default_configuration),
            ],
        )
        _inject_section(
            MigrationConfig,
            "migration_functions",
            MigrationConfig.default_config(),
            [("add_migration_function", MigrationConfig._add_migration_function)],
            True,
        )

    return _inject_core_sections


@pytest.fixture
def init_config(reset_configuration_singleton, inject_core_sections):
    def _init_config():
        reset_configuration_singleton()
        inject_core_sections()

        _Checker.add_checker(_ConfigIdChecker)
        _Checker.add_checker(_CoreSectionChecker)
        _Checker.add_checker(_DataNodeConfigChecker)
        _Checker.add_checker(_JobConfigChecker)
        # We don't need to add _MigrationConfigChecker because it is run only when the Core service is run.
        _Checker.add_checker(_TaskConfigChecker)
        _Checker.add_checker(_ScenarioConfigChecker)

        Config.configure_core(read_entity_retry=0)
        Core._is_running = False

    return _init_config


@pytest.fixture
def init_notifier():
    def _init_notifier():
        Notifier._topics_registrations_list = {}

    return _init_notifier


@pytest.fixture
def init_managers():
    def _init_managers():
        _CycleManagerFactory._build_manager()._delete_all()
        _ScenarioManagerFactory._build_manager()._delete_all()
        _SequenceManagerFactory._build_manager()._delete_all()
        _JobManagerFactory._build_manager()._delete_all()
        _TaskManagerFactory._build_manager()._delete_all()
        _DataManagerFactory._build_manager()._delete_all()
        _VersionManagerFactory._build_manager()._delete_all()
        _SubmissionManagerFactory._build_manager()._delete_all()

    return _init_managers


@pytest.fixture
def init_orchestrator():
    def _init_orchestrator():
        if _OrchestratorFactory._orchestrator is None:
            _OrchestratorFactory._build_orchestrator()
        _OrchestratorFactory._build_dispatcher()
        _OrchestratorFactory._orchestrator.jobs_to_run = Queue()
        _OrchestratorFactory._orchestrator.blocked_jobs = []

    return _init_orchestrator


@pytest.fixture(scope="function", autouse=True)
def cleanup_files():
    clean_files()
    yield
    clean_files()


def clean_files():
    output_dir = pathlib.Path(__file__).parent.resolve() / "outputs"
    if output_dir.exists():
        for f in output_dir.iterdir():
            os.remove(f)
    if os.path.exists(".data"):
        shutil.rmtree(".data", ignore_errors=True)
    if os.path.exists(".my_data"):
        shutil.rmtree(".my_data", ignore_errors=True)


@pytest.fixture(scope="function", autouse=True)
def clean_repository(init_config, init_managers, init_orchestrator, init_notifier):
    clean_files()
    init_config()
    close_all_sessions()
    init_orchestrator()
    init_managers()
    init_config()
    init_notifier()

    yield


@pytest.fixture(scope="function")
def sql_engine():
    return create_engine("sqlite:///:memory:")


@pytest.fixture
def tmp_sqlite(tmpdir_factory):
    fn = tmpdir_factory.mktemp("db")
    return os.path.join(fn.strpath, "test.db")


@pytest.fixture(scope="function")
def init_sql_repo(tmp_sqlite):
    Config.configure_core(repository_type="sql", repository_properties={"db_location": tmp_sqlite})

    # Clean SQLite database
    if _SQLConnection._connection:
        _SQLConnection._connection.close()
        _SQLConnection._connection = None
    _SQLConnection.init_db()

    return tmp_sqlite
