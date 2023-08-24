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
from time import sleep

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split


def sum(a, b):
    a = a["number"]
    b = b["number"]
    return a + b


def subtract(a, b):
    a = a["number"]
    b = b["number"]
    return a - b


def mult(a, b):
    return a * b


def mult_by_2(a):
    return a


def divide(a, b):
    return a / b


def average(a):
    return [a.sum() / len(a)]


def div_constant_with_sleep(a):
    sleep(1)
    return a["number"] / 10


def return_a_number():
    return 10


def return_a_number_with_sleep():
    sleep(1)
    return 10


def preprocess_dataset(initial_dataset: pd.DataFrame, date: dt.datetime = None):
    """This function preprocess the dataset to be used in the model
    Args:
        initial_dataset (pd.DataFrame): the raw format when we first read the data
    Returns:
        pd.DataFrame: the preprocessed dataset for classification
    """
    print("\n     Preprocessing the dataset...")

    # We filter the dataframe on the date
    if date != "None":
        initial_dataset["Date"] = pd.to_datetime(initial_dataset["Date"])
        processed_dataset = initial_dataset[initial_dataset["Date"] <= date]
        print(len(processed_dataset))
    else:
        processed_dataset = initial_dataset

    processed_dataset = processed_dataset[
        [
            "CreditScore",
            "Geography",
            "Gender",
            "Age",
            "Tenure",
            "Balance",
            "NumOfProducts",
            "HasCrCard",
            "IsActiveMember",
            "EstimatedSalary",
            "Exited",
        ]
    ]

    processed_dataset = pd.get_dummies(processed_dataset)

    if "Gender_Female" in processed_dataset.columns:
        processed_dataset.drop("Gender_Female", axis=1, inplace=True)

    processed_dataset = processed_dataset.apply(pd.to_numeric)

    columns_to_select = [
        "CreditScore",
        "Age",
        "Tenure",
        "Balance",
        "NumOfProducts",
        "HasCrCard",
        "IsActiveMember",
        "EstimatedSalary",
        "Geography_France",
        "Geography_Germany",
        "Geography_Spain",
        "Gender_Male",
        "Exited",
    ]

    processed_dataset = processed_dataset[[col for col in columns_to_select if col in processed_dataset.columns]]

    print("     Preprocessing done!\n")
    return processed_dataset


def create_train_test_data(preprocessed_dataset: pd.DataFrame):
    """This function will create the train data by segmenting the dataset
    Args:
        preprocessed_dataset (pd.DataFrame): the preprocessed dataset
    Returns:
        pd.DataFrame: the training dataset
    """
    print("\n     Creating the training and testing dataset...")

    X_train, X_test, y_train, y_test = train_test_split(
        preprocessed_dataset.iloc[:, :-1], preprocessed_dataset.iloc[:, -1], test_size=0.2, random_state=42
    )

    train_data = pd.concat([X_train, y_train], axis=1)
    test_data = pd.concat([X_test, y_test], axis=1)
    print("     Creating done!")
    return train_data, test_data


def train_model_baseline(train_dataset: pd.DataFrame):
    """Function to train the Logistic Regression model
    Args:
        train_dataset (pd.DataFrame): the training dataset
    Returns:
        model (LogisticRegression): the fitted model
    """
    print("     Training the model...\n")
    X, y = train_dataset.iloc[:, :-1], train_dataset.iloc[:, -1]
    model_fitted = LogisticRegression().fit(X, y)
    print("\n    ", model_fitted, " is trained!")

    importance_dict = {"Features": X.columns, "Importance": model_fitted.coef_[0]}
    importance = pd.DataFrame(importance_dict).sort_values(by="Importance", ascending=True)
    return model_fitted, importance


def train_model(train_dataset: pd.DataFrame):
    """Function to train the Logistic Regression model
    Args:
        train_dataset (pd.DataFrame): the training dataset
    Returns:
        model (RandomForest): the fitted model
    """
    print("     Training the model...\n")
    X, y = train_dataset.iloc[:, :-1], train_dataset.iloc[:, -1]
    model_fitted = RandomForestClassifier().fit(X, y)
    print("\n    ", model_fitted, " is trained!")

    importance_dict = {"Features": X.columns, "Importance": model_fitted.feature_importances_}
    importance = pd.DataFrame(importance_dict).sort_values(by="Importance", ascending=True)
    return model_fitted, importance


def forecast(test_dataset: pd.DataFrame, trained_model: RandomForestClassifier):
    """Function to forecast the test dataset
    Args:
        test_dataset (pd.DataFrame): the test dataset
        trained_model (LogisticRegression): the fitted model
    Returns:
        forecast (pd.DataFrame): the forecasted dataset
    """
    print("     Forecasting the test dataset...")
    X, y = test_dataset.iloc[:, :-1], test_dataset.iloc[:, -1]
    # predictions = trained_model.predict(X)
    predictions = trained_model.predict_proba(X)[:, 1]
    print("     Forecasting done!")
    return predictions


def forecast_baseline(test_dataset: pd.DataFrame, trained_model: LogisticRegression):
    """Function to forecast the test dataset
    Args:
        test_dataset (pd.DataFrame): the test dataset
        trained_model (LogisticRegression): the fitted model
    Returns:
        forecast (pd.DataFrame): the forecasted dataset
    """
    print("     Forecasting the test dataset...")
    X, y = test_dataset.iloc[:, :-1], test_dataset.iloc[:, -1]
    predictions = trained_model.predict_proba(X)[:, 1]
    print("     Forecasting done!")
    return predictions


def roc_from_scratch(probabilities, test_dataset, partitions=100):
    print("     Calculation of the ROC curve...")
    y_test = test_dataset.iloc[:, -1]

    roc = np.array([])
    for i in range(partitions + 1):
        threshold_vector = np.greater_equal(probabilities, i / partitions).astype(int)
        tpr, fpr = true_false_positive(threshold_vector, y_test)
        roc = np.append(roc, [fpr, tpr])

    roc_np = roc.reshape(-1, 2)
    roc_data = pd.DataFrame({"False positive rate": roc_np[:, 0], "True positive rate": roc_np[:, 1]})
    print("     Calculation done")
    print("     Scoring...")

    score_auc = roc_auc_score(y_test, probabilities)
    print("     Scoring done\n")

    return roc_data, score_auc


def true_false_positive(threshold_vector: np.array, y_test: np.array):
    """Function to calculate the true positive rate and the false positive rate

    Args:
        threshold_vector (np.array): the test dataset
        y_test (np.array): the fitted model
    Returns:
        tpr (pd.DataFrame): the forecasted dataset
        fpr (pd.DataFrame): the forecasted dataset
    """

    true_positive = np.equal(threshold_vector, 1) & np.equal(y_test, 1)
    true_negative = np.equal(threshold_vector, 0) & np.equal(y_test, 0)
    false_positive = np.equal(threshold_vector, 1) & np.equal(y_test, 0)
    false_negative = np.equal(threshold_vector, 0) & np.equal(y_test, 1)

    tpr = true_positive.sum() / (true_positive.sum() + false_negative.sum())
    fpr = false_positive.sum() / (false_positive.sum() + true_negative.sum())

    return tpr, fpr


def create_metrics(predictions: np.array, test_dataset: np.array):
    print("     Creating the metrics...")
    threshold = 0.5
    threshold_vector = np.greater_equal(predictions, threshold).astype(int)

    y_test = test_dataset.iloc[:, -1]

    true_positive = (np.equal(threshold_vector, 1) & np.equal(y_test, 1)).sum()
    true_negative = (np.equal(threshold_vector, 0) & np.equal(y_test, 0)).sum()
    false_positive = (np.equal(threshold_vector, 1) & np.equal(y_test, 0)).sum()
    false_negative = (np.equal(threshold_vector, 0) & np.equal(y_test, 1)).sum()

    f1_score = np.around(2 * true_positive / (2 * true_positive + false_positive + false_negative), decimals=2)
    accuracy = np.around(
        (true_positive + true_negative) / (true_positive + true_negative + false_positive + false_negative), decimals=2
    )
    dict_ftpn = {"tp": true_positive, "tn": true_negative, "fp": false_positive, "fn": false_negative}

    number_of_good_predictions = true_positive + true_negative
    number_of_false_predictions = false_positive + false_negative

    metrics = {
        "f1_score": f1_score,
        "accuracy": accuracy,
        "dict_ftpn": dict_ftpn,
        "number_of_predictions": len(predictions),
        "number_of_good_predictions": number_of_good_predictions,
        "number_of_false_predictions": number_of_false_predictions,
    }

    print("     Creating the metrics done!")
    return metrics


def create_results(forecast_values, test_dataset):
    forecast_series_proba = pd.Series(
        np.around(forecast_values, decimals=2), index=test_dataset.index, name="Probability"
    )
    forecast_series = pd.Series((forecast_values > 0.5).astype(int), index=test_dataset.index, name="Forecast")
    true_series = pd.Series(test_dataset.iloc[:, -1], name="Historical", index=test_dataset.index)
    index_series = pd.Series(range(len(true_series)), index=test_dataset.index, name="Id")

    results = pd.concat([index_series, forecast_series_proba, forecast_series, true_series], axis=1)
    return results
