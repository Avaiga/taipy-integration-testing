from pathlib import Path
import sys
import taipy.core as tp
from taipy.config import Config

from shared import *


@timer
def read_data_node(data_node):
    return data_node.read()


@timer
def write_data_node(data_node, input_data):
    data = algorithm(input_data)
    data_node.write(data)


row_counts = [10**3, 10**4, 10**5, 10**6]  # 1K to 1M rows

# Uncomment to test 10M rows - which may take a while to run
# row_counts.append(10**7)


def report(row_count: int):
    Config.configure_global_app(clean_entities_enabled=True)
    tp.clean_all_entities()
    Path("./input").mkdir(parents=True, exist_ok=True)
    Path("./output").mkdir(parents=True, exist_ok=True)

    print(f"🚀 {row_count:,} rows")
    dicts = get_list_of_dicts(row_count)
    objects = get_list_of_objects(row_count)

    print()
    print("📝 Without encoder / decoder")

    scenario = tp.create_scenario(scenario_cfg)

    input_data_node = scenario.input_dataset
    input_data_node.path = f"./input/input_dicts_{row_count}.json"

    write_data_node(input_data_node, dicts)
    read_data_node(input_data_node)

    print()
    print("📝 With encoder / decoder")

    scenario_2 = tp.create_scenario(scenario_cfg_2)

    input_data_node_2 = scenario_2.input_dataset_2
    input_data_node_2.path = f"./input/input_objects_{row_count}.json"

    write_data_node(input_data_node_2, objects)
    read_data_node(input_data_node_2)

    print()


if __name__ == "__main__":

    open("report.txt", "w").close()

    with open("report.txt", "a", encoding="utf-8") as f:
        # Uncomment to log into report.txt
        sys.stdout = f

        for row_size in row_counts:
            report(row_size)
