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

import datetime as dt
import os
import pathlib

from complex_application_algos import *
from taipy.config import Config, Frequency, Scope
from taipy.core.config.job_config import JobConfig


def build_skipped_jobs_config():

    input_config = Config.configure_data_node(id="input")
    intermediate_config = Config.configure_data_node(id="intermediate")
    output_config = Config.configure_data_node(id="output")
    task_config_1 = Config.configure_task("first", mult_by_2, input_config, intermediate_config, skippable=True)
    task_config_2 = Config.configure_task("second", mult_by_2, intermediate_config, output_config, skippable=True)
    pipeline_config = Config.configure_pipeline("pipeline", [task_config_1, task_config_2])

    return pipeline_config


def build_complex_required_file_paths():
    csv_path_inp = os.path.join(pathlib.Path(__file__).parent.resolve(), "shared_test_cases/data_sample/example.csv")
    excel_path_inp = os.path.join(pathlib.Path(__file__).parent.resolve(), "shared_test_cases/data_sample/example.xlsx")

    csv_path_sum = os.path.join(pathlib.Path(__file__).parent.resolve(), "shared_test_cases/data_sample/sum.csv")
    excel_path_sum = os.path.join(pathlib.Path(__file__).parent.resolve(), "shared_test_cases/data_sample/sum.xlsx")

    excel_path_out = os.path.join(pathlib.Path(__file__).parent.resolve(), "shared_test_cases/data_sample/res.xlsx")
    csv_path_out = os.path.join(pathlib.Path(__file__).parent.resolve(), "shared_test_cases/data_sample/res.csv")
    return csv_path_inp, excel_path_inp, csv_path_sum, excel_path_sum, excel_path_out, csv_path_out


def build_complex_config():
    (
        csv_path_inp,
        excel_path_inp,
        csv_path_sum,
        excel_path_sum,
        excel_path_out,
        csv_path_out,
    ) = build_complex_required_file_paths()

    inp_csv_dn_1 = Config.configure_csv_data_node("dn_csv_in_1", default_path=csv_path_inp)
    inp_csv_dn_2 = Config.configure_csv_data_node("dn_csv_in_2", default_path=csv_path_inp)

    inp_excel_dn_1 = Config.configure_excel_data_node("dn_excel_in_1", default_path=excel_path_inp, sheet_name="Sheet1")
    inp_excel_dn_2 = Config.configure_excel_data_node("dn_excel_in_2", default_path=excel_path_inp, sheet_name="Sheet1")

    placeholder = Config.configure_data_node(id="dn_placeholder", default_data=10)

    dn_csv_sum = Config.configure_csv_data_node("dn_sum_csv", default_path=csv_path_sum)
    dn_excel_sum = Config.configure_excel_data_node("dn_sum_excel", default_path=excel_path_sum, sheet_name="Sheet1")

    dn_subtract_csv_excel = Config.configure_pickle_data_node("dn_subtract_csv_excel")
    dn_mult = Config.configure_pickle_data_node("dn_mult")
    dn_div = Config.configure_pickle_data_node("dn_div")

    output_csv_dn = Config.configure_csv_data_node("csv_out", csv_path_out)
    output_excel_dn = Config.configure_excel_data_node("excel_out", excel_path_out)

    task_print_csv = Config.configure_task("task_print_csv", print, input=inp_csv_dn_1)
    task_print_excel = Config.configure_task("task_print_excel", print, input=inp_excel_dn_1)
    task_sum_csv = Config.configure_task("task_sum_csv", sum, input=[inp_csv_dn_2, inp_csv_dn_1], output=dn_csv_sum)
    task_sum_excel = Config.configure_task(
        "task_sum_excel", sum, input=[inp_excel_dn_2, inp_excel_dn_1], output=dn_excel_sum
    )

    task_subtract_csv_excel = Config.configure_task(
        "task_subtract_csv_excel", subtract, input=[dn_csv_sum, dn_excel_sum], output=dn_subtract_csv_excel
    )
    task_insert_placeholder = Config.configure_task("task_insert_placeholder", return_a_number, output=[placeholder])
    task_mult = Config.configure_task(
        "task_mult_by_placeholder", mult, input=[dn_subtract_csv_excel, placeholder], output=dn_mult
    )
    task_div = Config.configure_task("task_div_by_placeholder", divide, input=[dn_mult, placeholder], output=dn_div)
    task_avg_div = Config.configure_task("task_avg_div", average, input=dn_div, output=output_csv_dn)
    task_avg_mult = Config.configure_task("task_avg_mult", average, input=dn_mult, output=output_excel_dn)

    pipeline_sum_print_mul_print_avg_placeholder_mul = Config.configure_pipeline(
        "pipeline",
        [
            task_print_csv,
            task_print_excel,
            task_sum_csv,
            task_sum_excel,
            task_subtract_csv_excel,
            task_insert_placeholder,
            task_mult,
            task_div,
            task_avg_div,
            task_avg_mult,
        ],
    )

    scenario_config = Config.configure_scenario("scenario", [pipeline_sum_print_mul_print_avg_placeholder_mul])
    return scenario_config


def build_churn_classification_required_file_paths():
    csv_path_inp = os.path.join(pathlib.Path(__file__).parent.resolve(), "shared_test_cases/data_sample/churn.csv")
    return csv_path_inp


def build_churn_classification_config():
    csv_path_inp = build_churn_classification_required_file_paths()

    # path for csv and file_path for pickle
    initial_dataset = Config.configure_data_node(
        id="initial_dataset", path=csv_path_inp, storage_type="csv", has_header=True
    )

    date_cfg = Config.configure_data_node(id="date", default_data="None")

    preprocessed_dataset = Config.configure_data_node(
        id="preprocessed_dataset", cacheable=True, validity_period=dt.timedelta(days=1)
    )

    # the final datanode that contains the processed data
    train_dataset = Config.configure_data_node(id="train_dataset", cacheable=True, validity_period=dt.timedelta(days=1))

    # the final datanode that contains the processed data
    trained_model = Config.configure_data_node(id="trained_model", cacheable=True, validity_period=dt.timedelta(days=1))

    trained_model_baseline = Config.configure_data_node(
        id="trained_model_baseline", cacheable=True, validity_period=dt.timedelta(days=1)
    )

    # the final datanode that contains the processed data
    test_dataset = Config.configure_data_node(id="test_dataset", cacheable=True, validity_period=dt.timedelta(days=1))

    forecast_dataset = Config.configure_data_node(
        id="forecast_dataset", scope=Scope.SCENARIO, cacheable=True, validity_period=dt.timedelta(days=1)
    )

    roc_data = Config.configure_data_node(
        id="roc_data", scope=Scope.SCENARIO, cacheable=True, validity_period=dt.timedelta(days=1)
    )

    score_auc = Config.configure_data_node(
        id="score_auc", scope=Scope.SCENARIO, cacheable=True, validity_period=dt.timedelta(days=1)
    )

    metrics = Config.configure_data_node(
        id="metrics", scope=Scope.SCENARIO, cacheable=True, validity_period=dt.timedelta(days=1)
    )

    feature_importance_cfg = Config.configure_data_node(id="feature_importance", scope=Scope.SCENARIO)

    results = Config.configure_data_node(
        id="results", scope=Scope.SCENARIO, cacheable=True, validity_period=dt.timedelta(days=1)
    )

    ##############################################################################################################################
    # Creation of the tasks
    ##############################################################################################################################

    # the task will make the link between the input data node
    # and the output data node while executing the function

    # initial_dataset --> preprocess dataset --> preprocessed_dataset
    task_preprocess_dataset = Config.configure_task(
        id="preprocess_dataset",
        input=[initial_dataset, date_cfg],
        function=preprocess_dataset,
        output=preprocessed_dataset,
    )

    # preprocessed_dataset --> create train data --> train_dataset, test_dataset
    task_create_train_test = Config.configure_task(
        id="create_train_and_test_data",
        input=preprocessed_dataset,
        function=create_train_test_data,
        output=[train_dataset, test_dataset],
    )

    # train_dataset --> create train_model data --> trained_model
    task_train_model = Config.configure_task(
        id="train_model", input=train_dataset, function=train_model, output=[trained_model, feature_importance_cfg]
    )

    # train_dataset --> create train_model data --> trained_model
    task_train_model_baseline = Config.configure_task(
        id="train_model_baseline",
        input=train_dataset,
        function=train_model_baseline,
        output=[trained_model_baseline, feature_importance_cfg],
    )

    # test_dataset --> forecast --> forecast_dataset
    task_forecast = Config.configure_task(
        id="predict_the_test_data", input=[test_dataset, trained_model], function=forecast, output=forecast_dataset
    )

    # test_dataset --> forecast --> forecast_dataset
    task_forecast_baseline = Config.configure_task(
        id="predict_of_baseline",
        input=[test_dataset, trained_model_baseline],
        function=forecast_baseline,
        output=forecast_dataset,
    )

    task_roc = Config.configure_task(
        id="task_roc", input=[forecast_dataset, test_dataset], function=roc_from_scratch, output=[roc_data, score_auc]
    )

    task_roc_baseline = Config.configure_task(
        id="task_roc_baseline",
        input=[forecast_dataset, test_dataset],
        function=roc_from_scratch,
        output=[roc_data, score_auc],
    )

    task_create_metrics = Config.configure_task(
        id="task_create_metrics", input=[forecast_dataset, test_dataset], function=create_metrics, output=metrics
    )

    task_create_results = Config.configure_task(
        id="task_create_results", input=[forecast_dataset, test_dataset], function=create_results, output=results
    )

    ##############################################################################################################################
    # Creation of the pipeline and the scenario
    ##############################################################################################################################

    # configuration of the pipeline and scenario
    pipeline_preprocessing = Config.configure_pipeline(
        id="pipeline_preprocessing", task_configs=[task_preprocess_dataset, task_create_train_test]
    )

    pipeline_train_baseline = Config.configure_pipeline(
        id="pipeline_train_baseline", task_configs=[task_train_model_baseline]
    )
    pipeline_train_model = Config.configure_pipeline(id="pipeline_train_model", task_configs=[task_train_model])

    pipeline_model = Config.configure_pipeline(
        id="pipeline_model", task_configs=[task_forecast, task_roc, task_create_metrics, task_create_results]
    )

    pipeline_baseline = Config.configure_pipeline(
        id="pipeline_baseline",
        task_configs=[task_forecast_baseline, task_roc_baseline, task_create_metrics, task_create_results],
    )

    # the scenario will run the pipelines
    scenario_cfg = Config.configure_scenario(
        id="churn_classification",
        pipeline_configs=[
            pipeline_preprocessing,
            pipeline_train_baseline,
            pipeline_train_model,
            pipeline_model,
            pipeline_baseline,
        ],
        frequency=Frequency.WEEKLY,
    )

    return scenario_cfg
