import os
import pickle

import taipy.core as tp
from taipy.config import Config

from shared import *


def test_pickle():
    with open(PICKLE_DICT_INPUT_PATH, "rb") as f:
        dict_data = pickle.load(f)
    with open(PICKLE_LIST_INPUT_PATH, "rb") as f:
        list_data = pickle.load(f)

    Config.configure_global_app(clean_entities_enabled=True)
    tp.clean_all_entities()

    # 📝 List of dicts

    scenario_1 = tp.create_scenario(scenario_cfg_1)
    input_data_node_1 = scenario_1.input_dataset_1
    output_data_node_1 = scenario_1.output_dataset_1
    pipeline_1 = scenario_1.p1
    
    read_data_1 = input_data_node_1.read()
    assert len(read_data_1) == ROW_COUNT
    assert read_data_1 == dict_data
    
    assert output_data_node_1.read() is None
    output_data_node_1.write(read_data_1)
    assert dict_data == output_data_node_1.read()
    
    output_data_node_1.write(None)
    assert output_data_node_1.read() is None
    pipeline_1.submit()
    assert dict_data == output_data_node_1.read()
    
    output_data_node_1.write(None)
    assert output_data_node_1.read() is None
    scenario_1.submit()
    assert dict_data == output_data_node_1.read()
    
    os.remove(PICKLE_DICT_OUTPUT_PATH)

    # 📝 List of objects
    scenario_2 = tp.create_scenario(scenario_cfg_2)
    input_data_node_2 = scenario_2.input_dataset_2
    output_data_node_2 = scenario_2.output_dataset_2
    pipeline_2 = scenario_2.p2
    
    read_data_2 = input_data_node_2.read()
    assert len(read_data_2) == ROW_COUNT
    assert read_data_2 == list_data
    
    assert output_data_node_2.read() is None
    output_data_node_2.write(read_data_2)
    assert list_data == output_data_node_2.read()
    
    output_data_node_2.write(None)
    assert output_data_node_2.read() is None
    pipeline_2.submit()
    assert list_data == output_data_node_2.read()
    
    output_data_node_2.write(None)
    assert output_data_node_2.read() is None
    scenario_2.submit()
    assert list_data == output_data_node_2.read()
    
    os.remove(PICKLE_LIST_OUTPUT_PATH)
