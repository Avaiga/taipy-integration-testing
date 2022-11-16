from taipy.config.common.frequency import Frequency
from taipy.config.config import Config
from tests.pickle.shared.algorithms import algorithm

PICKLE_DICT_INPUT_PATH = "tests/pickle/input_dict_1000.p"
PICKLE_DICT_OUTPUT_PATH = "tests/pickle/output_dict_1000.p"
PICKLE_LIST_INPUT_PATH = "tests/pickle/input_object_1000.p"
PICKLE_LIST_OUTPUT_PATH = "tests/pickle/output_object_1000.p"
ROW_COUNT = 1000


input_dataset_cfg_1 = Config.configure_pickle_data_node(id="input_dataset_1", path=PICKLE_DICT_INPUT_PATH)
output_dataset_cfg_1 = Config.configure_pickle_data_node(
    id="output_dataset_1", path=PICKLE_DICT_OUTPUT_PATH)
task_cfg_1 = Config.configure_task(id="t1", input=input_dataset_cfg_1, function=algorithm, output=output_dataset_cfg_1)
pipeline_cfg_1 = Config.configure_pipeline(id="p1", task_configs=[task_cfg_1])
scenario_cfg_1 = Config.configure_scenario(id="s1", pipeline_configs=[
                                         pipeline_cfg_1], frequency=Frequency.DAILY)

input_dataset_cfg_2 = Config.configure_pickle_data_node(id="input_dataset_2", path=PICKLE_LIST_INPUT_PATH)
output_dataset_cfg_2 = Config.configure_pickle_data_node(
    id="output_dataset_2", path=PICKLE_LIST_OUTPUT_PATH)
task_cfg_2 = Config.configure_task(id="t2", input=input_dataset_cfg_2, function=algorithm, output=output_dataset_cfg_2)
pipeline_cfg_2 = Config.configure_pipeline(id="p2", task_configs=[task_cfg_2])
scenario_cfg_2 = Config.configure_scenario(id="s2", pipeline_configs=[
                                         pipeline_cfg_2], frequency=Frequency.DAILY)
