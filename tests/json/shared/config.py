from taipy.config.common.frequency import Frequency
from taipy.config.config import Config
from tests.json.shared.algorithms import algorithm
from tests.json.shared.utils import RowDecoder, RowEncoder

JSON_DICT_INPUT_PATH = "tests/json/input_dict_1000.json"
JSON_DICT_OUTPUT_PATH = "tests/json/output_dict_1000.json"
JSON_OBJECT_INPUT_PATH = "tests/json/input_object_1000.json"
JSON_OBJECT_OUTPUT_PATH = "tests/json/output_object_1000.json"
ROW_COUNT = 1000

input_dataset_cfg_1 = Config.configure_json_data_node(id="input_json_dataset_1", path=JSON_DICT_INPUT_PATH)
output_dataset_cfg_1 = Config.configure_json_data_node(
    id="output_json_dataset_1", path=JSON_DICT_OUTPUT_PATH)
task_cfg_1 = Config.configure_task(id="t1", input=input_dataset_cfg_1, function=algorithm, output=output_dataset_cfg_1)
pipeline_cfg_1 = Config.configure_pipeline(id="p1", task_configs=[task_cfg_1])
scenario_cfg_1 = Config.configure_scenario(id="s1", pipeline_configs=[
                                         pipeline_cfg_1], frequency=Frequency.DAILY)

input_dataset_cfg_2 = Config.configure_json_data_node(
    id="input_json_dataset_2", path=JSON_OBJECT_INPUT_PATH, decoder=RowDecoder)
output_dataset_cfg_2 = Config.configure_json_data_node(
    id="output_json_dataset_2", path=JSON_OBJECT_OUTPUT_PATH, encoder=RowEncoder, decoder=RowDecoder)
task_cfg_2 = Config.configure_task(id="t2", input=input_dataset_cfg_2, function=algorithm, output=output_dataset_cfg_2)
pipeline_cfg_2 = Config.configure_pipeline(id="p2", task_configs=[task_cfg_2])
scenario_cfg_2 = Config.configure_scenario(id="s2", pipeline_configs=[
    pipeline_cfg_2], frequency=Frequency.DAILY)
