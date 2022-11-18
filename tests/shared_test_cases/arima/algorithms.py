import random
from datetime import datetime
from typing import List
import time
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd


def train(historical_daily_temperature: pd.DataFrame):
    print('----- Started training -----')
    time.sleep(2)
    for _ in range(2):
        print('----- Model is in training -----')
    return ARIMA(endog=historical_daily_temperature['Temp'].to_numpy(), order=(1, 1, 0)).fit()


def predict(model, dates: List[datetime]) -> List[List[float]]:
    res = [t + random.uniform(0, 3) for t in model.forecast(len(dates))]
    return {'result': res}
