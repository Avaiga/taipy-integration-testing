from pathlib import Path
import dataclasses

from taipy.config.common.frequency import Frequency
from taipy.config.config import Config

from tests.excel.shared.algorithms import algorithm

EXCEL_INPUT_PATH = "tests/excel/input_1000_multi_sheets.xlsx"
EXCEL_OUTPUT_PATH = "tests/excel/output_1000.xlsx"
ROW_COUNT = 1000
SHEET_NAMES = ["Sheet 0", "Sheet 1", "Sheet 2", "Sheet 3", "Sheet 4", "Sheet 5"]

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

Config.unblock_update()

input_dataset_cfg_1 = Config.configure_excel_data_node(id="input_excel_multi_sheet_dataset_1", path=EXCEL_INPUT_PATH, has_header=True, sheet_name=SHEET_NAMES)
output_dataset_cfg_1 = Config.configure_excel_data_node(id="output_excel_multi_sheet_dataset_1", path=EXCEL_OUTPUT_PATH, has_header=True, sheet_name=SHEET_NAMES)
task_cfg = Config.configure_task(id="t1", input=input_dataset_cfg_1, function=algorithm, output=output_dataset_cfg_1)
pipeline_cfg = Config.configure_pipeline(id="p1", task_configs=[task_cfg])
scenario_cfg = Config.configure_scenario(id="s1", pipeline_configs=[
                                         pipeline_cfg], frequency=Frequency.DAILY)

input_dataset_cfg_2 = Config.configure_excel_data_node(
    id="input_excel_multi_sheet_dataset_2", path=EXCEL_INPUT_PATH, has_header=True, exposed_type=Row, sheet_name=SHEET_NAMES)
output_dataset_cfg_2 = Config.configure_excel_data_node(
    id="output_excel_multi_sheet_dataset_2", path=EXCEL_OUTPUT_PATH, has_header=True, exposed_type=Row, sheet_name=SHEET_NAMES)
task_cfg_2 = Config.configure_task(id="t2", input=input_dataset_cfg_2, function=algorithm, output=output_dataset_cfg_2)
pipeline_cfg_2 = Config.configure_pipeline(id="p2", task_configs=[task_cfg_2])
scenario_cfg_2 = Config.configure_scenario(id="s2", pipeline_configs=[
    pipeline_cfg_2], frequency=Frequency.DAILY)

input_dataset_cfg_3 = Config.configure_excel_data_node(
    id="input_excel_multi_sheet_dataset_3", path=EXCEL_INPUT_PATH, has_header=True, exposed_type="numpy", sheet_name=SHEET_NAMES)
output_dataset_cfg_3 = Config.configure_excel_data_node(
    id="output_excel_multi_sheet_dataset_3", path=EXCEL_OUTPUT_PATH, has_header=True, exposed_type="numpy", sheet_name=SHEET_NAMES)
task_cfg_3 = Config.configure_task(id="t3", input=input_dataset_cfg_3, function=algorithm, output=output_dataset_cfg_3)
pipeline_cfg_3 = Config.configure_pipeline(id="p3", task_configs=[task_cfg_3])
scenario_cfg_3 = Config.configure_scenario(id="s3", pipeline_configs=[
    pipeline_cfg_3], frequency=Frequency.DAILY)

input_dataset_cfg_4 = Config.configure_excel_data_node(
    id="input_excel_multi_sheet_dataset_4", path=EXCEL_INPUT_PATH, has_header=True, exposed_type="modin", sheet_name=SHEET_NAMES)
output_dataset_cfg_4 = Config.configure_excel_data_node(
    id="output_excel_multi_sheet_dataset_4", path=EXCEL_OUTPUT_PATH, has_header=True, exposed_type="modin", sheet_name=SHEET_NAMES)
task_cfg_4 = Config.configure_task(id="t4", input=input_dataset_cfg_4, function=algorithm, output=output_dataset_cfg_4)
pipeline_cfg_4 = Config.configure_pipeline(id="p4", task_configs=[task_cfg_4])
scenario_cfg_4 = Config.configure_scenario(id="s4", pipeline_configs=[
    pipeline_cfg_4], frequency=Frequency.DAILY)