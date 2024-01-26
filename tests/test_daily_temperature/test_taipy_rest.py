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
from typing import Optional

from flask_testing import TestCase
from taipy.rest import Rest
from .config import build_arima_config


class BaseTestCase(TestCase):
    def create_app(self):
        rest = Rest()
        rest._app.config["TESTING"] = True
        return rest._app


class RestTest(BaseTestCase):
    CSV_INPUT_PATH = os.path.join(pathlib.Path(__file__).parent.resolve(), "dataset", "daily-min-temperatures.csv")
    XLSX_OUTPUT_PATH = os.path.join(pathlib.Path(__file__).parent.parent.resolve(), "outputs", "output.xlsx")

    def _create(self, entity: str, config_id: str):
        return self.client.post(f"/api/v1/{entity}?config_id={config_id}")

    def _get(self, entity: str, id: Optional[str] = None):
        url = f"/api/v1/{entity}"
        if id:
            url = f"{url}/{id}"
        return self.client.get(url)

    def test_create_scenario_should_create_every_entity(self):
        build_arima_config(self.CSV_INPUT_PATH, self.XLSX_OUTPUT_PATH)

        response = self._create("scenarios", "Arima_scenario")
        assert response.status_code == 201
        assert response.json["message"] == "Scenario was created."

        all_scenarios = self._get("scenarios")
        all_data_nodes = self._get("datanodes")
        all_tasks = self._get("tasks")

        assert len(all_scenarios.json) == 1
        assert len(all_data_nodes.json) == 4
        assert len(all_tasks.json) == 2

    def test_submit_scenario(self):
        build_arima_config(self.CSV_INPUT_PATH, self.XLSX_OUTPUT_PATH)

        response = self._create("scenarios", "Arima_scenario")
        assert response.status_code == 201
        scenario_id = response.json["scenario"]["id"]

        response = self.client.post(f"/api/v1/scenarios/submit/{scenario_id}")
        assert response.status_code == 200
        assert response.json == {"message": f"Scenario {scenario_id} was submitted."}

        all_jobs = self._get("jobs")
        for jb in all_jobs.json:
            assert jb["status"] == "Status.COMPLETED"
