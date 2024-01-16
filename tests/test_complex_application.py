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
from unittest.mock import patch

import pandas as pd
import taipy.core.taipy as tp
from taipy.config import Config
from taipy.core import Core
from taipy.core.config.job_config import JobConfig
from taipy.core.job.status import Status
from taipy.core.submission.submission_status import SubmissionStatus

from .complex_application_configs import (
    average,
    build_churn_classification_config,
    build_complex_config,
    build_complex_required_file_paths,
    build_skipped_jobs_config,
)
from .utils import assert_true_after_time


def test_skipped_jobs():
    scenario_config = build_skipped_jobs_config()

    with patch("sys.argv", ["prog"]):
        core = Core()
        core.run()

        scenario = tp.create_scenario(scenario_config)
        scenario.input_dn.write(2)
        scenario.submit()
        assert len(tp.get_jobs()) == 2
        for job in tp.get_jobs():
            assert job.status == Status.COMPLETED

        scenario.submit()
        assert len(tp.get_jobs()) == 4
        skipped = []
        for job in tp.get_jobs():
            if job.status != Status.COMPLETED:
                assert job.status == Status.SKIPPED
                skipped.append(job)
        assert len(skipped) == 2
        core.stop()


def test_complex_development():
    # d1 --- t1
    # |
    # | --- t2 --- d5 --- |                   t10 --- d12
    #        |            |                   |
    #        |            |                   |
    #        d2           | --- t5 --- d7 --- t7 --- d9 --- t8 --- d10 --- t9 --- d11
    #                     |                   |             |
    # d3 --- |            |                   |             |
    # |      |            |     t6 --- d8 -------------------
    # |      t3 --- d6 ---|
    # |      |
    # |      |
    # t4     d4

    _, _, csv_path_sum, excel_path_sum, excel_path_out, csv_path_out = build_complex_required_file_paths()
    scenario_config = build_complex_config()

    with patch("sys.argv", ["prog"]):
        core = Core()
        core.run(force_restart=True)

        scenario = tp.create_scenario(scenario_config)

        tp.submit(scenario)

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

        core.stop()


def test_complex_standlone():
    # d1 --- t1
    # |
    # | --- t2 --- d5 --- |                   t10 --- d12
    #        |            |                   |
    #        |            |                   |
    #        d2           | --- t5 --- d7 --- t7 --- d9 --- t8 --- d10 --- t9 --- d11
    #                     |                   |             |
    # d3 --- |            |                   |             |
    # |      |            |     t6 --- d8 -------------------
    # |      t3 --- d6 ---|
    # |      |
    # |      |
    # t4     d4

    _, _, csv_path_sum, excel_path_sum, excel_path_out, csv_path_out = build_complex_required_file_paths()
    scenario_config = build_complex_config()
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)

    with patch("sys.argv", ["prog"]):
        core = Core()

        core.run(force_restart=True)

        scenario = tp.create_scenario(scenario_config)

        jobs = tp.submit(scenario)

        assert_true_after_time(lambda: os.path.exists(csv_path_out) and os.path.exists(excel_path_out))
        assert_true_after_time(lambda: tp.get(jobs[0].submit_id).submission_status == SubmissionStatus.COMPLETED)

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

        core.stop()


def test_churn_classification_development():
    scenario_cfg = build_churn_classification_config()

    with patch("sys.argv", ["prog"]):
        core = Core()
        core.run(force_restart=True)

        scenario = tp.create_scenario(scenario_cfg)
        jobs = tp.submit(scenario)

        assert_true_after_time(lambda: tp.get(jobs[0].submit_id).submission_status == SubmissionStatus.COMPLETED)

        core.stop()


def test_churn_classification_standalone():
    scenario_cfg = build_churn_classification_config()
    Config.configure_job_executions(mode=JobConfig._STANDALONE_MODE, max_nb_of_workers=2)

    with patch("sys.argv", ["prog"]):
        core = Core()
        core.run(force_restart=True)

        scenario = tp.create_scenario(scenario_cfg)
        jobs = tp.submit(scenario)

        assert_true_after_time(lambda: os.path.exists(scenario.results._path))
        assert_true_after_time(lambda: tp.get(jobs[0].submit_id).submission_status == SubmissionStatus.COMPLETED)

        core.stop()
