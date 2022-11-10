from pathlib import Path
import dataclasses

from taipy.config.common.frequency import Frequency
from taipy.config.config import Config

from .algorithms import algorithm

CSV_INPUT_PATH = "tests/csv/input_1000.csv"
CSV_OUTPUT_PATH = "tests/csv/output_1000.csv"

@dataclasses.dataclass
class Row:
    id: int
    age: int
    rating: float
    
    def __post_init__(self):
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                setattr(self, field.name, field.type(value))


input_dataset_cfg = Config.configure_csv_data_node(id="input_dataset_1", path=CSV_INPUT_PATH, has_header=True)
output_dataset_cfg = Config.configure_csv_data_node(id="output_dataset_1", path=CSV_OUTPUT_PATH, has_header=True)
task_cfg = Config.configure_task(id="t1", input=input_dataset_cfg, function=algorithm, output=output_dataset_cfg)
pipeline_cfg = Config.configure_pipeline(id="p1", task_configs=[task_cfg])
scenario_cfg = Config.configure_scenario(id="s1", pipeline_configs=[
                                         pipeline_cfg], frequency=Frequency.DAILY)

input_dataset_cfg_2 = Config.configure_csv_data_node(
    id="input_dataset_2", path=CSV_INPUT_PATH, has_header=True, exposed_type=Row)
output_dataset_cfg_2 = Config.configure_csv_data_node(
    id="output_dataset_2", path=CSV_OUTPUT_PATH, has_header=True, exposed_type=Row)
task_cfg_2 = Config.configure_task(id="t2", input=input_dataset_cfg_2, function=algorithm, output=output_dataset_cfg_2)
pipeline_cfg_2 = Config.configure_pipeline(id="p2", task_configs=[task_cfg_2])
scenario_cfg_2 = Config.configure_scenario(id="s2", pipeline_configs=[
    pipeline_cfg_2], frequency=Frequency.DAILY)

input_dataset_cfg_3 = Config.configure_csv_data_node(
    id="input_dataset_3", path=CSV_INPUT_PATH, has_header=True, exposed_type="numpy")
output_dataset_cfg_3 = Config.configure_csv_data_node(
    id="output_dataset_3", path=CSV_OUTPUT_PATH, has_header=True, exposed_type="numpy")
task_cfg_3 = Config.configure_task(id="t3", input=input_dataset_cfg_3, function=algorithm, output=output_dataset_cfg_3)
pipeline_cfg_3 = Config.configure_pipeline(id="p3", task_configs=[task_cfg_3])
scenario_cfg_3 = Config.configure_scenario(id="s3", pipeline_configs=[
    pipeline_cfg_3], frequency=Frequency.DAILY)

input_dataset_cfg_4 = Config.configure_csv_data_node(
    id="input_dataset_4", path=CSV_INPUT_PATH, has_header=True, exposed_type="modin")
output_dataset_cfg_4 = Config.configure_csv_data_node(
    id="output_dataset_4", path=CSV_OUTPUT_PATH, has_header=True, exposed_type="modin")
task_cfg_4 = Config.configure_task(id="t4", input=input_dataset_cfg_4, function=algorithm, output=output_dataset_cfg_4)
pipeline_cfg_4 = Config.configure_pipeline(id="p4", task_configs=[task_cfg_4])
scenario_cfg_4 = Config.configure_scenario(id="s4", pipeline_configs=[
    pipeline_cfg_4], frequency=Frequency.DAILY)