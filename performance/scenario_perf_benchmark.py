from pathlib import Path
import sys

import taipy as tp
from taipy import Config
from taipy.config.common.scope import Scope
from taipy.config.scenario.scenario_config import ScenarioConfig

from utils import algorithm, timer
from perf_benchmark_abstract import PerfBenchmarkAbstract

class ScenarioPerfBenchmark(PerfBenchmarkAbstract):
    
    BENCHMARK_REPORT_FILE_NAME = "scenario_benchmark_report.csv"
    DEFAULT_ENTITY_COUNTS = [10**2, 10**3, 10**4]
    MULTI_ENTITY_TYPES = ["datanode", "task", "pipeline", "scenario"]
    DATA_NODE_SCOPES = [Scope.PIPELINE, Scope.SCENARIO, Scope.CYCLE, Scope.GLOBAL]
    
    def __init__(self, entity_counts: list[int] = None, report_path: str = None):
        super().__init__(report_path=report_path, folder_path=Path(__file__).parent.resolve())

        self.entity_counts = entity_counts if entity_counts else self.DEFAULT_ENTITY_COUNTS.copy()

    def run(self):
        with open(self.report_path, "a", encoding="utf-8") as f:
            sys.stdout = f
            for test_parameters in self._generate_test_parameter_list():
                self._run_test(test_parameters)

    def _generate_test_parameter_list(self) -> list:
        test_parameter_list = []
        
        for entity_count in self.entity_counts:
            for multi_entity_type in self.MULTI_ENTITY_TYPES:
                for data_node_scope in self.DATA_NODE_SCOPES:
                    test_parameter_list.append((entity_count, multi_entity_type, data_node_scope))
        return test_parameter_list

    def _run_test(self, test_parameters: dict):
        entity_count, multi_entity_type, data_node_scope = test_parameters[0], test_parameters[1], test_parameters[2]

        properties_as_str = [str(entity_count), str(multi_entity_type), str(data_node_scope)]
        scenario_cfg = self._generate_configs(entity_count, multi_entity_type, data_node_scope)
        create_scenario, create_scenario_multiple_times = self._generate_methods(properties_as_str)
        if multi_entity_type == "scenario":
            create_scenario_multiple_times(entity_count, scenario_cfg)
        else:
            create_scenario(scenario_cfg)

    @staticmethod
    def _generate_methods(properties_as_str):
        
        @timer(properties_as_str)
        def create_scenario(scenario_config: ScenarioConfig):
            return tp.create_scenario(scenario_config)
        
        @timer(properties_as_str)
        def create_scenario_multiple_times(entity_count: int, scenario_config: ScenarioConfig):
            scenarios = []
            for _ in range(entity_count):
                scenarios.append(tp.create_scenario(scenario_config))
            return scenarios
        
        return create_scenario, create_scenario_multiple_times
        
    def _generate_configs(self, entity_count, multi_entity_type: str = "datanode", data_node_scope: Scope = Scope.PIPELINE):
        Config.unblock_update()
        Config.configure_global_app(clean_entities_enabled=True)
        tp.clean_all_entities()
        
        nb_dn = entity_count if multi_entity_type == "datanode" else 1
        nb_task = entity_count if multi_entity_type == "task" else 1
        nb_pipeline = entity_count if multi_entity_type == "pipeline" else 1
        
        input_datanode_cfgs = []
        task_cfgs = []
        pipeline_cfgs = []
        
        for i in range(nb_dn):
            input_datanode_cfgs.append(Config.configure_data_node(id=f"input_datanode_{i}", scope=data_node_scope))
        
        output_datanode_cfg = [Config.configure_data_node(id="output_datanode", scope=data_node_scope)]
        
        for i in range(nb_task):
            task_cfgs.append(Config.configure_task(id=f"task_{i}", input=input_datanode_cfgs, function=algorithm,
                                                   output=output_datanode_cfg))
        
        for i in range(nb_pipeline):
            pipeline_cfgs.append(Config.configure_pipeline(id=f"pipeline_{i}", task_configs=task_cfgs))

        scenario_cfg = Config.configure_scenario(id="scenario", pipeline_configs=pipeline_cfgs)
        
        return scenario_cfg

