import os
from pathlib import Path

from taipy.config.common.frequency import Frequency
from taipy.config.config import Config
from .algorithms import algorithm

FOLDER_PATH = Path(__file__).parent.resolve()
INPUT_FOLDER_PATH = os.path.join(FOLDER_PATH, "inputs")
OUTPUT_FOLDER_PATH = os.path.join(FOLDER_PATH, "outputs")


def generate_configs(rows: int, **kwargs):
    input_datanode_cfg = Config.configure_csv_data_node(id="input_datanode", path=f"{INPUT_FOLDER_PATH}/input_{rows}.csv", **kwargs)
    output_datanode_cfg = Config.configure_csv_data_node(id="output_datanode", path=f"{OUTPUT_FOLDER_PATH}/output_{rows}.csv", **kwargs)
    task_cfg = Config.configure_task(id="task", input=input_datanode_cfg, function=algorithm, output=output_datanode_cfg)
    pipeline_cfg = Config.configure_pipeline(id="pipeline", task_configs=[task_cfg])
    scenario_cfg = Config.configure_scenario(id="scenario", pipeline_configs=[
                                            pipeline_cfg], frequency=Frequency.DAILY)
    return scenario_cfg
