import pytest
import os
import shutil


@pytest.fixture(autouse=True)
def cleanup_data():
    from time import sleep

    sleep(0.1)
    if os.path.exists(".data"):
        shutil.rmtree(".data", ignore_errors=True)
    if os.path.exists("test.db"):
        os.remove("test.db")

    init_scheduler()
    init_managers()
    init_config()


def init_config():
    from taipy import Config
    from taipy.config import IssueCollector
    from taipy.config._config import _Config
    from taipy.config._toml_serializer import _TomlSerializer

    Config.unblock_update()
    Config._default_config = _Config()._default_config()
    Config._python_config = _Config()
    Config._file_config = None
    Config._env_file_config = None
    Config._applied_config = _Config._default_config()
    Config._collector = IssueCollector()
    Config._serializer = _TomlSerializer()


def init_managers():
    from taipy.core.scenario._scenario_manager import _ScenarioManager
    from taipy.core.pipeline._pipeline_manager import _PipelineManager
    from taipy.core.data._data_manager import _DataManager
    from taipy.core.task._task_manager import _TaskManager
    from taipy.core.job._job_manager import _JobManager
    from taipy.core.cycle._cycle_manager import _CycleManager

    _ScenarioManager._delete_all()
    _PipelineManager._delete_all()
    _DataManager._delete_all()
    _TaskManager._delete_all()
    _JobManager._delete_all()
    _CycleManager._delete_all()


def init_scheduler():
    from taipy.core._scheduler._scheduler_factory import _SchedulerFactory
    from queue import Queue

    if _SchedulerFactory._scheduler is None:
        _SchedulerFactory._build_scheduler()
    _SchedulerFactory._build_dispatcher()
    _SchedulerFactory._scheduler.jobs_to_run = Queue()
    _SchedulerFactory._scheduler.blocked_jobs = []
