from shared_test_cases.arima.config import *

import taipy as tp


def test_submit_scenario_submit_success():
    scenario = tp.create_scenario(arima_scenario_config)
    tp.submit(scenario)

    assert scenario.forecast_values.read() is not None
    assert len(tp.get_pipelines()) == 1
    assert len(tp.get_tasks()) == 2
    assert len(tp.get_jobs()) == 2
    assert len(tp.get_data_nodes()) == 4
