import os
import shutil
from pathlib import Path

from utils import timer
from perf_benchmark_abstract import PerfBenchmarkAbstract

import taipy as tp
from taipy.core.data import Operator, JoinOperator
from taipy.core.config import ScenarioConfig


class DataPerfBenchmark(PerfBenchmarkAbstract):

    DEFAULT_ROW_COUNTS = [10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7]

    def __init__(self, row_counts: list[int] = None, report_path: str = None, folder_path: str = None):
        self.row_counts = row_counts if row_counts else self.DEFAULT_ROW_COUNTS.copy()
        
        super().__init__(report_path=report_path, folder_path=folder_path)
        
        self.input_folder_path = os.path.join(self.folder_path, "inputs")
        self.output_folder_path = os.path.join(self.folder_path, "outputs")
        Path(str(self.input_folder_path)).mkdir(parents=True, exist_ok=True)
        Path(str(self.output_folder_path)).mkdir(parents=True, exist_ok=True)
        

    def __del__(self):
        super().__del__()
        shutil.rmtree(self.input_folder_path)
        shutil.rmtree(self.output_folder_path)
    
    def _generate_prop_sets(self):
        return self.prop_dicts
    
    @staticmethod
    def _generate_entities(prefix: str, scenario_cfg: ScenarioConfig):
        scenario = tp.create_scenario(scenario_cfg)
        input_data_node = scenario.data_nodes[prefix + "_input_datanode"]
        output_data_node = scenario.data_nodes[prefix + "_output_datanode"]
        pipeline = scenario.pipelines[prefix + "_pipeline"]
        return input_data_node, output_data_node, pipeline, scenario
    
    @staticmethod
    def _generate_methods(properties_as_str):        
        @timer(properties_as_str)
        def read_data_node(data_node):
            return data_node.read()

        @timer(properties_as_str)
        def filter_data_node(data_node):
            return data_node.filter([("age", 50, Operator.GREATER_OR_EQUAL)])
        
        @timer(properties_as_str)
        def join_filter_data_node(data_node):
            return data_node.filter([("age", 10, Operator.GREATER_OR_EQUAL), ("age", 40, Operator.LESS_OR_EQUAL)], JoinOperator.AND)
        
        @timer(properties_as_str)
        def write_data_node(data_node, data):
            data_node.write(data)

        @timer(properties_as_str)
        def submit_pipeline(pipeline):
            pipeline.submit()

        @timer(properties_as_str)
        def submit_scenario(scenario):
            scenario.submit()

        return read_data_node, filter_data_node, join_filter_data_node, write_data_node, submit_pipeline, submit_scenario
