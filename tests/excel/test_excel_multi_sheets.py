import os
import pandas as pd
import modin.pandas as modin_pd
import numpy as np
import pytest

import taipy.core as tp
from taipy.config import Config

def test_excel_multi_sheet():
    from tests.excel.shared.multi_sheet_config import (
        scenario_cfg,
        scenario_cfg_2,
        scenario_cfg_3,
        scenario_cfg_4,
        EXCEL_INPUT_PATH,
        EXCEL_OUTPUT_PATH,
        SHEET_NAMES,
        ROW_COUNT,
        Row
    )
    
    pandas_data = pd.read_excel(EXCEL_INPUT_PATH, sheet_name=SHEET_NAMES)
    numpy_data = {sheet_name: pandas_data[sheet_name].to_numpy() for sheet_name in SHEET_NAMES}
    modin_data = modin_pd.read_excel(EXCEL_INPUT_PATH, sheet_name=SHEET_NAMES)
    custom_data = {}
    for sheet_name in SHEET_NAMES:
        rows = []
        for _, row in pandas_data[sheet_name].iterrows():
            rows.append(Row(int(row.id), int(row.age), float(row.rating)))
        custom_data[sheet_name] = rows
    
    Config.configure_global_app(clean_entities_enabled=True)
    tp.clean_all_entities()

    # 📊 Without exposed type (pandas is the default exposed type)

    scenario_1 = tp.create_scenario(scenario_cfg)
    input_data_node_1 = scenario_1.input_dataset_1
    output_data_node_1 = scenario_1.output_dataset_1
    pipeline_1 = scenario_1.p1

    read_data_1 = input_data_node_1.read()
    assert len(read_data_1) == len(SHEET_NAMES)
    assert all([pandas_data[sheet_name].equals(read_data_1[sheet_name]) for sheet_name in SHEET_NAMES])
    
    assert output_data_node_1.read() is None
    output_data_node_1.write(read_data_1)
    assert len(output_data_node_1.read()) == len(SHEET_NAMES)
    assert all([pandas_data[sheet_name].equals(output_data_node_1.read()[sheet_name]) for sheet_name in SHEET_NAMES])
    
    output_data_node_1.write(None)
    # No sheetname
    with pytest.raises(ValueError):
        assert output_data_node_1.read()
    pipeline_1.submit()
    assert all([pandas_data[sheet_name].equals(output_data_node_1.read()[sheet_name]) for sheet_name in SHEET_NAMES])
    
    output_data_node_1.write(None)
    # No sheetname
    with pytest.raises(ValueError):
        assert output_data_node_1.read()
    scenario_1.submit()
    assert all([pandas_data[sheet_name].equals(output_data_node_1.read()[sheet_name]) for sheet_name in SHEET_NAMES])
    
    os.remove(EXCEL_OUTPUT_PATH)

    # 📊 With custom class as exposed type
    
    def compare_custom_date(read_data, custom_data):
        return [row_1.id == row_2.id and row_1.age == row_2.age and row_1.rating == row_2.rating for row_1, row_2 in zip(read_data, custom_data)]
    
    scenario_2 = tp.create_scenario(scenario_cfg_2)
    input_data_node_2 = scenario_2.input_dataset_2
    output_data_node_2 = scenario_2.output_dataset_2
    pipeline_2 = scenario_2.p2
    
    read_data_2 = input_data_node_2.read()
    assert len(read_data_2) == len(SHEET_NAMES)
    assert all(compare_custom_date(read_data_2[sheet_name], custom_data[sheet_name]) for sheet_name in SHEET_NAMES)
    
    output_data_node_2.write(read_data_2)
    assert len(read_data_2) == len(SHEET_NAMES)
    # print(output_data_node_2.read())    #TODO: failed write function
    # assert all(compare_custom_date(read_data_2[sheet_name], output_data_node_2.read()[sheet_name]) for sheet_name in SHEET_NAMES)
    
    # output_data_node_2.write(None)
    # assert isinstance(output_data_node_2.read(), list)
    # assert len(output_data_node_2.read()) == 0
    # pipeline_2.submit()
    # assert all(compare_custom_date(read_data_2[sheet_name], output_data_node_2.read()[sheet_name]) for sheet_name in SHEET_NAMES)
    
    # output_data_node_2.write(None)
    # assert isinstance(output_data_node_2.read(), list)
    # assert len(output_data_node_2.read()) == 0
    # scenario_2.submit()
    # assert all(compare_custom_date(read_data_2[sheet_name], output_data_node_2.read()[sheet_name]) for sheet_name in SHEET_NAMES)

    os.remove(EXCEL_OUTPUT_PATH)

    # # 📊 With numpy as exposed type
    scenario_3 = tp.create_scenario(scenario_cfg_3)
    input_data_node_3 = scenario_3.input_dataset_3
    output_data_node_3 = scenario_3.output_dataset_3
    pipeline_3 = scenario_3.p3
    
    read_data_3 = input_data_node_3.read()
    assert len(read_data_3) == len(SHEET_NAMES)
    assert [np.array_equal(read_data_3[sheet_name], numpy_data[sheet_name]) for sheet_name in SHEET_NAMES]
    

    assert output_data_node_3.read() is None
    output_data_node_3.write(read_data_3)
    assert len(output_data_node_3.read()) == len(SHEET_NAMES)
    assert [np.array_equal(read_data_3[sheet_name], output_data_node_3.read()[sheet_name]) for sheet_name in SHEET_NAMES]

    output_data_node_3.write(None)
    with pytest.raises(ValueError):
        assert output_data_node_1.read()
    pipeline_3.submit()
    assert [np.array_equal(read_data_3[sheet_name], output_data_node_3.read()[sheet_name]) for sheet_name in SHEET_NAMES]
    
    output_data_node_3.write(None)
    with pytest.raises(ValueError):
        assert output_data_node_1.read()
    scenario_3.submit()
    assert [np.array_equal(read_data_3[sheet_name], output_data_node_3.read()[sheet_name]) for sheet_name in SHEET_NAMES]
    
    os.remove(EXCEL_OUTPUT_PATH)
    
    # # 📊 With modin as exposed type
    scenario_4 = tp.create_scenario(scenario_cfg_4)
    input_data_node_4 = scenario_4.input_dataset_4
    output_data_node_4 = scenario_4.output_dataset_4
    pipeline_4 = scenario_4.p4

    read_data_4 = input_data_node_4.read()
    assert len(read_data_4) == len(SHEET_NAMES)
    assert all([modin_data[sheet_name].equals(read_data_4[sheet_name]) for sheet_name in SHEET_NAMES])
    
    assert output_data_node_4.read() is None
    output_data_node_4.write(read_data_4)
    assert len(read_data_4) == len(SHEET_NAMES)
    assert all([modin_data[sheet_name].equals(output_data_node_4.read()[sheet_name]) for sheet_name in SHEET_NAMES])
    
    output_data_node_4.write(None)
    with pytest.raises(ValueError):
        output_data_node_4.read()   #TODO: test excel file has no header provided
    pipeline_4.submit()
    assert all([modin_data[sheet_name].equals(output_data_node_4.read()[sheet_name]) for sheet_name in SHEET_NAMES])
    
    output_data_node_4.write(None)
    with pytest.raises(ValueError):
        output_data_node_4.read()   #TODO: test excel file has no header provided
    scenario_4.submit()
    assert all([modin_data[sheet_name].equals(output_data_node_4.read()[sheet_name]) for sheet_name in SHEET_NAMES])
    
    os.remove(EXCEL_OUTPUT_PATH)
