import sys
from pathlib import Path
import random
import json

import taipy as tp
from taipy import Config

from utils import Row, RowEncoder, RowDecoder, algorithm
from perf_benchmark import PerfBenchmark

class JsonPerfBenchmark(PerfBenchmark):

    BENCHMARK_REPORT_FILE_NAME = "json_data_node_benchmark_report.csv"

    def __init__(self, report_path: str = None):
        self.type_formats = ['list_dict', 'list_object']
        self.prop_dicts = [
            {},
            {"encoder": RowEncoder, "decoder": RowDecoder},
        ]
        super().__init__(report_path=report_path, folder_path=Path(__file__).parent.resolve())

    def run(self):
        with open(self.report_path, "a", encoding="utf-8") as f:
            sys.stdout = f
            for row_count in self.row_counts:
                for type_format, properties in zip(self.type_formats, self._generate_prop_sets()):
                    self._generate_input_file(row_count, type_format)
                    self._run_test(row_count, type_format, properties)

    @staticmethod
    def __gen_list_of_dict_input_json(n):
        data = []
        for i in range(n):
            row = {"id": i+1,
                "age": random.randint(10, 99),
                "rating": round(random.uniform(0, 10), 2)
                }
            data.append(row)
        return data

    @staticmethod
    def __gen_list_of_objects_input_json(n):
        data = []
        for i in range(n):
            row = Row(i+1, random.randint(10, 99), round(random.uniform(0, 10), 2))
            data.append(row)
        return data

    def _generate_input_file(self, rows, type_format: str):
        path = f"{self.input_folder_path}/input_{type_format}_{rows}.json"
        if type_format == 'list_dict':
            data = self.__gen_list_of_dict_input_json(rows)
            encoder = None
        if type_format == 'list_object':
            data = self.__gen_list_of_objects_input_json(rows)
            encoder = RowEncoder
        json.dump(data, open(path, "w"), indent=4, cls=encoder)

    def _generate_prop_sets(self):
        return self.prop_dicts

    def _run_test(self, row_count: int, type_format: str, properties):
        def to_str(val):
            return "with_custom_encoder" if val else "without_custom_encoder"

        properties_as_str = [to_str(properties)]
        prefix = '_'.join(properties_as_str)
        properties_as_str.append(str(row_count))
        
        scenario_cfg = self._generate_configs(prefix, row_count, type_format, **properties)
        input_data_node, output_data_node, pipeline, scenario = self._generate_entities(prefix, scenario_cfg)
        read_data_node, write_data_node, submit_pipeline, submit_scenario = self._generate_methods(properties_as_str)
        data = read_data_node(input_data_node)
        write_data_node(output_data_node, data)
        submit_pipeline(pipeline)
        submit_scenario(scenario)

    def _generate_configs(self, prefix: str, row_count: int, type_format: str, **kwargs):
        Config.unblock_update()
        Config.configure_global_app(clean_entities_enabled=True)
        tp.clean_all_entities()

        input_datanode_cfg = Config.configure_json_data_node(id=prefix + "_input_datanode",
                                                            path=f"{self.input_folder_path}/input_{type_format}_{row_count}.json", **kwargs)
        output_datanode_cfg = Config.configure_json_data_node(id=prefix + "_output_datanode",
                                                             path=f"{self.output_folder_path}/output_{type_format}_{row_count}.json", **kwargs)
        task_cfg = Config.configure_task(id=prefix + "_task", input=input_datanode_cfg, function=algorithm,
                                         output=output_datanode_cfg)
        pipeline_cfg = Config.configure_pipeline(id=prefix + "_pipeline", task_configs=[task_cfg])
        scenario_cfg = Config.configure_scenario(id=prefix + "_scenario", pipeline_configs=[pipeline_cfg])
        return scenario_cfg
