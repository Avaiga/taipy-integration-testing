import os
import shutil
import sys
from pathlib import Path
import random

import taipy as tp
from taipy import Config
from taipy.core.config import ScenarioConfig

from utils import Row, algorithm, timer


class CSVPerfBenchmark:

    def __init__(self, report_path: str):
        self.row_counts = [10 ** 3, 10 ** 4] #, 10 ** 5, 10 ** 6, 10 ** 7]
        self.prop_dicts = [
            {"exposed_type": "pandas"},
            {"exposed_type": Row},
            {"exposed_type": "numpy"},
            {"exposed_type": "modin"},
        ]

        self.report_path = report_path
        folder_path = Path(__file__).parent.resolve()
        self.input_folder_path = os.path.join(folder_path, "inputs")
        self.output_folder_path = os.path.join(folder_path, "outputs")

        Path(str(self.input_folder_path)).mkdir(parents=True, exist_ok=True)
        Path(str(self.output_folder_path)).mkdir(parents=True, exist_ok=True)

    def __del__(self):
        shutil.rmtree(self.input_folder_path)
        shutil.rmtree(self.output_folder_path)

    def run(self):
        with open(self.report_path, "a", encoding="utf-8") as f:
            sys.stdout = f
            for row_count in self.row_counts:
                self._generate_input_file(row_count)
                for properties in self._generate_prop_sets():
                    self._run_test(row_count, properties)

    def _generate_input_file(self, rows):
        path = f"{self.input_folder_path}/input_{rows}.csv"
        col_names = ["id", "age", "rating"]
        lines = [",".join(col_names)]
        for i in range(rows):
            lines.append(f"{i + 1},{random.randint(1, 99)},{round(random.uniform(0, 10), 2)}")
        with open(path, "w+") as f:
            f.write("\n".join(lines))

    def _generate_prop_sets(self):
        return self.prop_dicts

    def _run_test(self, row_count: int, properties):
        def to_str(val):
            return val if isinstance(val, str) else val.__name__

        properties_as_str = list(map(to_str, properties.values()))
        properties_as_str.append(str(row_count))
        prefix = '_'.join(properties_as_str)

        scenario_cfg = self._generate_configs(prefix, row_count, **properties)
        input_data_node, output_data_node, pipeline, scenario = self._generate_entities(prefix, scenario_cfg)
        read_data_node, write_data_node, submit_pipeline, submit_scenario = self._generate_methods(properties_as_str)

        data = read_data_node(input_data_node)
        write_data_node(output_data_node, data)
        submit_pipeline(pipeline)
        submit_scenario(scenario)

    def _generate_configs(self, prefix: str, row_count: int, **kwargs):
        Config.unblock_update()
        Config.configure_global_app(clean_entities_enabled=True)
        tp.clean_all_entities()
        input_datanode_cfg = Config.configure_csv_data_node(id=prefix + "_input_datanode",
                                                            path=f"{self.input_folder_path}/input_{row_count}.csv", **kwargs)
        output_datanode_cfg = Config.configure_csv_data_node(id=prefix + "_output_datanode",
                                                             path=f"{self.output_folder_path}/output_{row_count}.csv", **kwargs)
        task_cfg = Config.configure_task(id=prefix + "_task", input=input_datanode_cfg, function=algorithm,
                                         output=output_datanode_cfg)
        pipeline_cfg = Config.configure_pipeline(id=prefix + "_pipeline", task_configs=[task_cfg])
        scenario_cfg = Config.configure_scenario(id=prefix + "_scenario", pipeline_configs=[pipeline_cfg])
        return scenario_cfg

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
        def write_data_node(data_node, data):
            data_node.write(data)

        @timer(properties_as_str)
        def submit_pipeline(pipeline):
            pipeline.submit()

        @timer(properties_as_str)
        def submit_scenario(scenario):
            scenario.submit()
        return read_data_node, write_data_node, submit_pipeline, submit_scenario
