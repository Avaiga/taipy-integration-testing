from taipy.config.common.frequency import Frequency
from taipy.config.config import Config
from .algorithms import algorithm
from .utils import RowDecoder, RowEncoder

JSON_INPUT_PATH = "tests/json/input_1000.csv"
JSON_OUTPUT_PATH = "tests/json/output_1000.csv"
ROW_COUNT = 1000

input_dataset_cfg = Config.configure_json_data_node(id="input_dataset", path=JSON_INPUT_PATH)
output_dataset_cfg = Config.configure_json_data_node(
    id="output_dataset", path=JSON_OUTPUT_PATH)
task_cfg = Config.configure_task(id="t1", input=input_dataset_cfg, function=algorithm, output=output_dataset_cfg)
pipeline_cfg = Config.configure_pipeline(id="p1", task_configs=[task_cfg])
scenario_cfg = Config.configure_scenario(id="s1", pipeline_configs=[
                                         pipeline_cfg], frequency=Frequency.DAILY)

input_dataset_cfg_2 = Config.configure_json_data_node(
    id="input_dataset_2", path=JSON_INPUT_PATH, encoder=RowEncoder)
output_dataset_cfg_2 = Config.configure_json_data_node(
    id="output_dataset_2", path=JSON_OUTPUT_PATH, decoder=RowDecoder)
task_cfg_2 = Config.configure_task(id="t2", input=input_dataset_cfg_2, function=algorithm, output=output_dataset_cfg_2)
pipeline_cfg_2 = Config.configure_pipeline(id="p2", task_configs=[task_cfg_2])
scenario_cfg_2 = Config.configure_scenario(id="s2", pipeline_configs=[
    pipeline_cfg_2], frequency=Frequency.DAILY)
