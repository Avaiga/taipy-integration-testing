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

from taipy.config import Config, Frequency

from .algorithms import *


def build_churn_config(dataset_path):
    """Build a scenario config for the Churn algorithm."""
    ##################################################################################################################
    # Creation of the data nodes
    ##################################################################################################################
    # the initial datanode that contains the raw data. Scenario Input.
    initial_dataset = Config.configure_csv_data_node(id="initial_dataset", default_path=dataset_path, has_header=True)
    # the datanode that contains the date. Scenario Input.
    date_cfg = Config.configure_pickle_data_node(id="date", default_data="None")

    # the datanode that contains the processed data. Output of the preprocess task.
    preprocessed_dataset = Config.configure_data_node(id="preprocessed_dataset", validity_period=dt.timedelta(days=1))

    # the train dataset datanode that contains 80% of the data. Output the split task.
    train_dataset = Config.configure_data_node(id="train_dataset", validity_period=dt.timedelta(days=1))
    # the test dataset datanode that contains 20% of the data. Output the split task.
    test_dataset = Config.configure_data_node(id="test_dataset", validity_period=dt.timedelta(days=1))

    # The trained model. Output of the train task.
    model = Config.configure_data_node(id="trained_model", validity_period=dt.timedelta(days=1))
    # The trained model for the baseline algorithm. Output of the train_baseline task.
    model_baseline = Config.configure_data_node(id="trained_model_baseline", validity_period=dt.timedelta(days=1))
    # The feature importance. Output of the train task and the train_baseline task.
    feature_importance = Config.configure_data_node(id="feature_importance")

    # The predictions using test dataset. Output of the predict task.
    predictions_test = Config.configure_data_node(id="forecast_test_dataset")
    # The predictions using test dataset for the baseline algorithm. Output of the predict_baseline task.
    predictions_test_baseline = Config.configure_data_node(id="forecast_baseline_dataset")

    # The roc data. Output of the compute roc task and the compute roc for baseline task.
    roc_data = Config.configure_data_node(id="roc_data")
    # The score auc. Output of the compute roc task and the compute roc for baseline task.
    score_auc = Config.configure_data_node(id="score_auc")
    # The metrics. Output of the compute metrics task and the compute metrics for baseline task.
    metrics = Config.configure_data_node(id="metrics")
    # The results. Output of the compute results task and the compute results for baseline task.
    results = Config.configure_data_node(id="results")

    ##################################################################################################################
    # Creation of the tasks
    ##################################################################################################################
    # initial_dataset, date_cfg --> preprocess --> preprocessed_dataset
    task_preprocess = Config.configure_task(
        id="preprocess",
        input=[initial_dataset, date_cfg],
        function=preprocess,
        output=preprocessed_dataset,
    )

    # preprocessed_dataset --> split --> train_dataset, test_dataset
    task_split = Config.configure_task(
        id="split",
        input=preprocessed_dataset,
        function=split,
        output=[train_dataset, test_dataset],
    )

    # train_dataset --> train --> model, feature_importance
    task_train = Config.configure_task(
        id="train",
        input=train_dataset,
        function=train,
        output=[model, feature_importance],
    )

    # train_dataset --> train_baseline --> model_baseline, feature_importance
    task_train_baseline = Config.configure_task(
        id="train_baseline",
        input=train_dataset,
        function=train_baseline,
        output=[model_baseline, feature_importance],
    )

    # test_dataset, model --> predict --> predictions_test
    task_predict = Config.configure_task(
        id="predict",
        input=[test_dataset, model],
        function=forecast,
        output=predictions_test,
    )

    # test_dataset, model_baseline --> predict_baseline --> predictions_test_baseline
    task_forecast_baseline = Config.configure_task(
        id="predict_baseline",
        input=[test_dataset, model_baseline],
        function=predict_baseline,
        output=predictions_test_baseline,
    )

    # predictions_test, test_dataset --> compute_roc --> roc_data, score_auc
    task_roc = Config.configure_task(
        id="compute_roc",
        input=[predictions_test, test_dataset],
        function=compute_roc,
        output=[roc_data, score_auc],
    )

    # predictions_test_baseline, test_dataset --> compute_roc_baseline --> roc_data, score_auc
    task_roc_baseline = Config.configure_task(
        id="compute_roc_baseline",
        input=[predictions_test_baseline, test_dataset],
        function=compute_roc,
        output=[roc_data, score_auc],
    )

    # predictions_test, test_dataset --> compute_metrics --> metrics
    task_create_metrics = Config.configure_task(
        id="compute_metrics",
        input=[predictions_test, test_dataset],
        function=compute_metrics,
        output=metrics,
    )

    # predictions_test_baseline, test_dataset --> compute_metrics --> metrics
    task_create_baseline_metrics = Config.configure_task(
        id="compute_metrics_baseline",
        input=[predictions_test_baseline, test_dataset],
        function=compute_metrics,
        output=metrics,
    )

    # predictions_test, test_dataset --> compute_results --> results
    task_create_results = Config.configure_task(
        id="compute_results",
        input=[predictions_test, test_dataset],
        function=compute_results,
        output=results,
    )

    # predictions_test_baseline, test_dataset --> compute_results --> results
    task_create_baseline_results = Config.configure_task(
        id="compute_results_baseline",
        input=[predictions_test_baseline, test_dataset],
        function=compute_results,
        output=results,
    )

    ##################################################################################################################
    # Creation of the scenario
    ##################################################################################################################
    # the scenario will run the sequences
    scenario_cfg = Config.configure_scenario(
        id="churn_classification",
        task_configs=[
            task_preprocess,
            task_split,
            task_train_baseline,
            task_train,
            task_predict,
            task_roc,
            task_create_metrics,
            task_create_results,
            task_forecast_baseline,
            task_roc_baseline,
            task_create_metrics,
            task_create_results,
            task_create_baseline_metrics,
            task_create_baseline_results,
        ],
        frequency=Frequency.WEEKLY,
    )

    return scenario_cfg
