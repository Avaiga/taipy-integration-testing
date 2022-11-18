from pathlib import Path
import shutil
import sys

import taipy.core as tp
from taipy.config import Config

from shared.config import generate_configs, INPUT_FOLDER_PATH, OUTPUT_FOLDER_PATH, FOLDER_PATH
from shared.utils import timer, gen_input_csv
from shared.algorithms import Row


row_counts = [10**3, 10**4, 10**5, 10**6]  # 1K to 1M rows
properties = [
    {"exposed_type": "pandas"},
    {"exposed_type": Row},
    {"exposed_type": "numpy"},
    {"exposed_type": "modin"},
]


def summarize(row_count, exposed_type):
    @timer(row_count, exposed_type)
    def read_data_node(data_node):
        return data_node.read()
    @timer(row_count, exposed_type)
    def write_data_node(data_node, data):
        data_node.write(data)
    @timer(row_count, exposed_type)
    def submit_pipeline(pipeline):
        pipeline.submit()
    @timer(row_count, exposed_type)
    def submit_scenario(scenario):
        scenario.submit()
        
    return read_data_node, write_data_node, submit_pipeline, submit_scenario


def report(row_count: int):
    Config.configure_global_app(clean_entities_enabled=True)
    tp.clean_all_entities()

    gen_input_csv(INPUT_FOLDER_PATH, row_count)

    for p in properties:
        scenario_cfg = generate_configs(row_count, **p)
        
        scenario = tp.create_scenario(scenario_cfg)
        input_data_node = scenario.input_datanode
        output_data_node = scenario.output_datanode
        pipeline = scenario.pipeline
        
        exposed_type = p['exposed_type']
        read_data_node, write_data_node, submit_pipeline, submit_scenario = summarize(
            row_count, 
            exposed_type if isinstance(exposed_type, str) else exposed_type.__name__
        )

        read_data = read_data_node(input_data_node)
        write_data_node(output_data_node, read_data)
        submit_pipeline(pipeline)
        submit_scenario(scenario)


if __name__ == "__main__":

    Path(str(OUTPUT_FOLDER_PATH)).mkdir(parents=True, exist_ok=True)
    Path(str(INPUT_FOLDER_PATH)).mkdir(parents=True, exist_ok=True)

    with open(f"{FOLDER_PATH.parent.resolve()}/report.csv", "a", encoding="utf-8") as f:
        sys.stdout = f
        for row_size in row_counts:
            report(row_size)

    shutil.rmtree(INPUT_FOLDER_PATH)
    shutil.rmtree(OUTPUT_FOLDER_PATH)
