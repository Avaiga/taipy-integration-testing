import random
from datetime import datetime
from typing import List
import time
import pandas as pd


def failing_job(historical_daily_temperature: pd.DataFrame):
    time.sleep(2)
    print('----- Prepared to raise exception -----')
    raise Exception


def predict(model, dates: List[datetime]) -> List[List[float]]:
    res = [t + random.uniform(0, 3) for t in model.forecast(len(dates))]
    return {'result': res}
