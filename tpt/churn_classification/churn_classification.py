import os
import pathlib

import taipy.core.taipy as tp
from taipy import SubmissionStatus, Config
from taipy.core import Core
from taipy.core.config import JobConfig

from .config import build_churn_config
from .utils import message, assert_true_after_time, init_sql_repo

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _run():
    dataset_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "dataset", "churn_10000.csv")

    scn_config = build_churn_config(dataset_path)
    core = Core()
    core.run(force_restart=True)
    scenario = tp.create_scenario(scn_config)

    for inpt in scenario.get_inputs():
        assert inpt.is_ready_for_reading

    submission = tp.submit(scenario)

    assert_true_after_time(
        lambda: submission.submission_status == SubmissionStatus.COMPLETED,
        time=300,
        msg=lambda s: message(s, 300),
        s=submission,
    )
    core.stop()


if __name__ == "__main__":
    logger.info("----------------------Running Churn Classification----------------------")
    # test development fs repo
    logger.info("----------------------Test Development FS REPO----------------------")
    _run()

    # test standalone fs repo
    logger.info("----------------------Test Standalone FS REPO----------------------")
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=4)
    _run()

    # test development sql repo
    logger.info("----------------------Test Development SQL REPO----------------------")
    Config.configure_job_executions(mode=JobConfig._DEVELOPMENT_MODE, max_nb_of_workers=4)
    init_sql_repo()
    _run()

    # test standalone sql repo
    logger.info("----------------------Test Standalone SQL REPO----------------------")
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=4)
    init_sql_repo()
    _run()
