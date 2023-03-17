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
from pathlib import Path
from typing import Optional
from queue import Queue

import taipy as tp
from taipy.logger._taipy_logger import _TaipyLogger
from taipy.config import Config
from taipy.config._config import _Config
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config._serializer._toml_serializer import _TomlSerializer
from taipy.config.checker._checker import _Checker
from taipy.config.checker._checkers._gLobal_config_checker import _GlobalConfigChecker
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
)
from taipy.core._scheduler._scheduler_factory import _SchedulerFactory


from _blob_manager import _BlobManager

class PerfBenchmarkAbstract:

    logger = _TaipyLogger._get_logger()

    BENCHMARK_REPORT_FILE_NAME: Optional[str]
    BENCHMARK_FOLDER_NAME: str = "benchmark_results"

    def __init__(self, report_path: str = None):
        Config.unblock_update()
        Config.configure_global_app(clean_entities_enabled=True)

        self.folder_path: Path = Path(__file__).parent.resolve()

        benchmark_folder_path: str = os.path.join(self.folder_path, self.BENCHMARK_FOLDER_NAME)
        self.report_path: str = (
            report_path if report_path else os.path.join(benchmark_folder_path, self.BENCHMARK_REPORT_FILE_NAME)  # type: ignore
        )

        Path(str(benchmark_folder_path)).mkdir(parents=True, exist_ok=True)

        if self.__is_prod:
            _BlobManager.download_file(self.BENCHMARK_REPORT_FILE_NAME, self.report_path)
        
        self.core = tp.Core()
        self.core.run(force_restart=True)

    @property
    def __is_prod(self):
        return os.getenv("TAIPY_PERFORMANCE_BENCHMARK") == "0"

    def __del__(self):        
        if self.__is_prod:
            _BlobManager.upload_file(self.BENCHMARK_REPORT_FILE_NAME, self.report_path)
        

    def run(self):
        ...

    def clean_test_state(self):
        tp.clean_all_entities()
        self.clean_config()
        self.clean_scheduler()

    @property
    def BENCHMARK_NAME(self):
        raise NotImplementedError

    def log_header(self):
        self.logger.info("----------------------------------------------")
        self.logger.info("---  " + self.BENCHMARK_NAME.center(36) + "  ---")
        self.logger.info("----------------------------------------------")

    def clean_config(self):
        Config.unblock_update()
        Config._default_config = _Config()._default_config()
        Config._python_config = _Config()
        Config._file_config = None
        Config._env_file_config = None
        Config._applied_config = _Config._default_config()
        Config._collector = IssueCollector()
        Config._serializer = _TomlSerializer()
        _Checker._checkers = [_GlobalConfigChecker]

        from taipy.core.config import _inject_section

        _inject_section(
            JobConfig, "job_config", JobConfig("development"), [("configure_job_executions", JobConfig._configure)]
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
        _Checker.add_checker(_JobConfigChecker)
        _Checker.add_checker(_DataNodeConfigChecker)
        _Checker.add_checker(_TaskConfigChecker)
        _Checker.add_checker(_PipelineConfigChecker)
        _Checker.add_checker(_ScenarioConfigChecker)
        
    def clean_scheduler(self):
        self.core.stop()
        
        _SchedulerFactory._scheduler.jobs_to_run = Queue()
        _SchedulerFactory._scheduler.blocked_jobs = []
