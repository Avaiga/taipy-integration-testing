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

import random
import time
from datetime import datetime
from typing import Dict, List

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA


def train(historical_daily_temperature: pd.DataFrame):
    return ARIMA(endog=historical_daily_temperature["Temp"].to_numpy(), order=(1, 1, 0)).fit()


def predict(model, dates: List[datetime]) -> Dict[str, List]:
    res = [t + random.uniform(0, 3) for t in model.forecast(len(dates))]
    return {"result": res}
