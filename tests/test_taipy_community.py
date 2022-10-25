import datetime as dt
from shared.config import *

import taipy.core as tp


def test_submit_scenario_repository():
        Config.configure_global_app(clean_entities_enabled=True)

        scenario = tp.create_scenario(arima_scenario_config)
        tp.submit(scenario)

        assert scenario.forecast_values.read() is not None
        assert len(tp.get_pipelines()) == 1
        assert len(tp.get_data_nodes()) == 4
        assert len(tp.get_tasks()) == 2
        assert len(tp.get_jobs()) == 2
