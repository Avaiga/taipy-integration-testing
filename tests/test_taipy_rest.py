from typing import Optional

from flask_testing import TestCase
from taipy.rest import Rest

from shared.config import *


class BaseTestCase(TestCase):
    def create_app(self):
        rest = Rest()
        rest._app.config["TESTING"] = True
        return rest._app


class RestTest(BaseTestCase):
    def _create(self, entity: str, config_id: str):
        return self.client.post(f"/api/v1/{entity}?config_id={config_id}")
    
    def _get(self, entity: str, id: Optional[str] = None):
        url = f"/api/v1/{entity}"
        if id:
            url = f"{url}/{id}"
        return self.client.get(url)

    def test_create_scenario_should_create_every_entity(self):

        response = self._create("scenarios", "Arima_scenario")
        assert response.status_code == 201
        assert response.json["message"] == "Scenario was created."
        
        all_scenarios = self._get("scenarios")
        all_pipelines = self._get("pipelines")
        all_data_nodes = self._get("datanodes")
        all_tasks = self._get("tasks")

        assert len(all_scenarios.json) == 1
        assert len(all_pipelines.json) == 1
        assert len(all_data_nodes.json) == 4
        assert len(all_tasks.json) == 2
    
    def test_submit_scenario(self):
        response = self._create("scenarios", "Arima_scenario")
        assert response.status_code == 201
        scenario_id = response.json["scenario"]["id"]

        response = self.client.post(f"/api/v1/scenarios/submit/{scenario_id}")
        assert response.status_code == 200
        assert response.json == {'message': f'Scenario {scenario_id} was submitted.'}
        
        all_jobs = self._get("jobs")
        for jb in all_jobs.json:
            assert jb["status"] == 'Status.COMPLETED'
        
        
