import datetime as dt
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
import time


def preprocess(initial_dataset: pd.DataFrame, date: dt.datetime = None):
    """This function preprocess the dataset to be used in the model
    Args:
        initial_dataset (pd.DataFrame): the raw format when we first read the data
        date: the date to filter the dataset
    Returns:
        pd.DataFrame: the preprocessed dataset for classification
    """
    start = time.time()
    # We filter the dataframe on the date
    if date != "None":
        initial_dataset["Date"] = pd.to_datetime(initial_dataset["Date"])
        processed_dataset = initial_dataset[initial_dataset["Date"] <= date]
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
    print(f"{sys._getframe().f_code.co_name} - {time.time() - start}")
    return processed_dataset


def split(preprocessed_dataset: pd.DataFrame):
    """This function will create the train data by segmenting the dataset
    Args:
        preprocessed_dataset (pd.DataFrame): the preprocessed dataset
    Returns:
        pd.DataFrame: the training dataset
    """
    start = time.time()
    X_train, X_test, y_train, y_test = train_test_split(
        preprocessed_dataset.iloc[:, :-1], preprocessed_dataset.iloc[:, -1], test_size=0.2, random_state=42
    )
    train_data = pd.concat([X_train, y_train], axis=1)
    test_data = pd.concat([X_test, y_test], axis=1)
    print(f"{sys._getframe().f_code.co_name} - {time.time() - start}")
    return train_data, test_data


def train_baseline(train_dataset: pd.DataFrame):
    """Function to train the Logistic Regression model
    Args:
        train_dataset (pd.DataFrame): the training dataset
    Returns:
        model (LogisticRegression): the fitted model
    """
    start = time.time()
    X, y = train_dataset.iloc[:, :-1], train_dataset.iloc[:, -1]
    model_fitted = LogisticRegression(max_iter=300).fit(X, y)
    importance_dict = {"Features": X.columns, "Importance": model_fitted.coef_[0]}
    importance = pd.DataFrame(importance_dict).sort_values(by="Importance", ascending=True)
    print(f"{sys._getframe().f_code.co_name} - {time.time() - start}")
    return model_fitted, importance


def train(train_dataset: pd.DataFrame):
    """Function to train the Logistic Regression model
    Args:
        train_dataset (pd.DataFrame): the training dataset
    Returns:
        model (RandomForest): the fitted model
    """
    start = time.time()
    X, y = train_dataset.iloc[:, :-1], train_dataset.iloc[:, -1]
    model_fitted = RandomForestClassifier(n_estimators=50).fit(X, y)
    importance_dict = {"Features": X.columns, "Importance": model_fitted.feature_importances_}
    importance = pd.DataFrame(importance_dict).sort_values(by="Importance", ascending=True)
    print(f"{sys._getframe().f_code.co_name} - {time.time() - start}")
    return model_fitted, importance


def forecast(test_dataset: pd.DataFrame, trained_model: RandomForestClassifier):
    """Function to forecast the test dataset
    Args:
        test_dataset (pd.DataFrame): the test dataset
        trained_model (LogisticRegression): the fitted model
    Returns:
        forecast (pd.DataFrame): the forecasted dataset
    """
    start = time.time()
    X, y = test_dataset.iloc[:, :-1], test_dataset.iloc[:, -1]
    predictions = trained_model.predict_proba(X)[:, 1]
    print(f"{sys._getframe().f_code.co_name} - {time.time() - start}")
    return predictions


def predict_baseline(test_dataset: pd.DataFrame, trained_model: LogisticRegression):
    """Function to forecast the test dataset
    Args:
        test_dataset (pd.DataFrame): the test dataset
        trained_model (LogisticRegression): the fitted model
    Returns:
        forecast (pd.DataFrame): the forecasted dataset
    """
    start = time.time()
    X, y = test_dataset.iloc[:, :-1], test_dataset.iloc[:, -1]
    predictions = trained_model.predict_proba(X)[:, 1]
    print(f"{sys._getframe().f_code.co_name} - {time.time() - start}")
    return predictions


def compute_roc(probabilities, test_dataset, partitions=100):
    start = time.time()
    y_test = test_dataset.iloc[:, -1]

    roc = np.array([])
    for i in range(partitions + 1):
        threshold_vector = np.greater_equal(probabilities, i / partitions).astype(int)
        tpr, fpr = true_false_positive(threshold_vector, y_test)
        roc = np.append(roc, [fpr, tpr])

    roc_np = roc.reshape(-1, 2)
    roc_data = pd.DataFrame({"False positive rate": roc_np[:, 0], "True positive rate": roc_np[:, 1]})
    score_auc = roc_auc_score(y_test, probabilities)
    print(f"{sys._getframe().f_code.co_name} - {time.time() - start}")
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


def compute_metrics(predictions: np.array, test_dataset: np.array):
    start = time.time()
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
    print(f"{sys._getframe().f_code.co_name} - {time.time() - start}")
    return metrics


def compute_results(forecast_values, test_dataset):
    start = time.time()
    forecast_series_proba = pd.Series(
        np.around(forecast_values, decimals=2), index=test_dataset.index, name="Probability"
    )
    forecast_series = pd.Series((forecast_values > 0.5).astype(int), index=test_dataset.index, name="Forecast")
    true_series = pd.Series(test_dataset.iloc[:, -1], name="Historical", index=test_dataset.index)
    index_series = pd.Series(range(len(true_series)), index=test_dataset.index, name="Id")
    results = pd.concat([index_series, forecast_series_proba, forecast_series, true_series], axis=1)
    print(f"{sys._getframe().f_code.co_name} - {time.time() - start}")
    return results
