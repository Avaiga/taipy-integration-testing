import json
import os

import taipy.core as tp
from taipy.config import Config

from shared import *


def test_json():
    with open(JSON_DICT_INPUT_PATH, "r") as f:
        json_dict_data = json.load(f)
    with open(JSON_OBJECT_INPUT_PATH, "r") as f:
        json_object_data = json.load(f, cls=RowDecoder)
        
    Config.configure_global_app(clean_entities_enabled=True)
    tp.clean_all_entities()

    # 📝 Without encoder / decoder

    scenario_1 = tp.create_scenario(scenario_cfg_1)
    input_data_node_1 = scenario_1.input_dataset_1
    output_data_node_1 = scenario_1.output_dataset_1
    pipeline_1 = scenario_1.p1
    
    read_data_1 = input_data_node_1.read()
    assert len(read_data_1) == ROW_COUNT
    assert json_dict_data == read_data_1
    
    assert output_data_node_1.read() is None
    output_data_node_1.write(read_data_1)
    assert json_dict_data == output_data_node_1.read()
    
    output_data_node_1.write(None)
    assert output_data_node_1.read() is None
    pipeline_1.submit()
    assert json_dict_data == output_data_node_1.read()
    
    output_data_node_1.write(None)
    assert output_data_node_1.read() is None
    scenario_1.submit()
    assert json_dict_data == output_data_node_1.read()
    
    os.remove(JSON_DICT_OUTPUT_PATH)

    # 📝 With encoder / decoder

    def compare_custom_date(read_data, object_data):
        return [isinstance(row_1, Row) and row_1.id == row_2.id and row_1.age == row_2.age and row_1.rating == row_2.rating for row_1, row_2 in zip(read_data, object_data)]

    scenario_2 = tp.create_scenario(scenario_cfg_2)
    input_data_node_2 = scenario_2.input_dataset_2
    output_data_node_2 = scenario_2.output_dataset_2
    pipeline_2 = scenario_2.p2
    
    read_data_2 = input_data_node_2.read()
    assert len(read_data_2) == ROW_COUNT
    assert all(compare_custom_date(read_data_2, json_object_data))
    
    assert output_data_node_2.read() is None
    output_data_node_2.write(read_data_2)
    assert all(compare_custom_date(output_data_node_2.read(), json_object_data))
    
    output_data_node_2.write(None)
    assert output_data_node_2.read() is None
    pipeline_2.submit()
    assert all(compare_custom_date(output_data_node_2.read(), json_object_data))
    
    output_data_node_2.write(None)
    assert output_data_node_2.read() is None
    scenario_2.submit()
    assert all(compare_custom_date(output_data_node_2.read(), json_object_data))
    
    os.remove(JSON_OBJECT_OUTPUT_PATH)
