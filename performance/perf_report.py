# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
import os
from typing import List, Dict
import re
import pandas as pd
from taipy import Gui
from azure.storage.blob import BlobServiceClient


CONN_STR = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
CONTAINER = "benchmark-result"
# Create the BlobServiceClient object
blob_service_client = BlobServiceClient.from_connection_string(CONN_STR)


def extract_key(name: str) -> str:
    pattern = r'\/(.*?)_'
    match = re.search(pattern, name)
    key = match.group(1)
    return key if key != "data" else "data_node"


def __list_blobs() -> List[str]:
    container_client = blob_service_client.get_container_client(container=CONTAINER)
    return [b.name for b in container_client.list_blobs()]


def __download_blobs(blobs: List) -> None:
    for blob in blobs:
        os.makedirs(os.path.dirname(blob), exist_ok=True)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER, blob=blob)
        with open(blob, "wb") as my_blob:
            blob_data = blob_client.download_blob()
            blob_data.readinto(my_blob)


def __load_data() -> Dict[str, pd.DataFrame]:
    blobs = __list_blobs()
    __download_blobs(blobs)
    data = {}
    for blob in blobs:
        key = extract_key(blob)
        data[key] = pd.read_csv(blob)
    return data


data_storage = __load_data()


def on_change(state, var_name, var_value):
    state, function_names = generate_display_data(state)
    if var_name == "selected_dn_type":
        state.partial.update_content(
            state, create_partial_content(display_data=display_data, function_names=function_names, state=state)
        )


def create_partial_content(display_data=None, function_names=None, state=None):
    if state:
        col_to_line = col_to_lines[state.selected_dn_type]
    else:
        col_to_line = col_to_lines["json"]

    if function_names:
        function_names = ";".join(function_names)
    else:
        function_names = "read_data_node;write_data_node;submit_sequence;submit_scenario"

    partial_content = (
        """##Select function name: <center><|{selected_function_name}|toggle|lov="""
        + function_names
        + """|></center><|{display_data}|chart|mode=line|x=datetime|"""
        + col_to_line
        + """|>"""
    )
    return partial_content


def generate_display_data(state):
    data = data_storage[state.selected_dn_type]
    state.display_data = convert_data_to_display(data, state.selected_function_name)
    return state, data["function_name"].unique().tolist()


def convert_data_to_display(data, selected_function_name):
    data = data[data["function_name"] == selected_function_name]
    columns = ["datetime"]
    columns.extend(data["exposed_type"].unique())
    display_data = pd.DataFrame(columns=columns)

    for _, row in data.iterrows():
        if row["datetime"] in display_data["datetime"].unique():
            display_data.loc[display_data["datetime"] == row["datetime"], row["exposed_type"]] = row["time_elapsed"]
        else:
            new_row = {exposed_type: None for exposed_type in data["exposed_type"].unique()}
            new_row["datetime"] = row["datetime"]
            new_row[row["exposed_type"]] = row["time_elapsed"]
            display_data = display_data.append([new_row], ignore_index=True)
    return display_data


def on_change_entity(state):
    _entity = state.entity
    ds_repo_entity, functions = load_repo_data(_entity, state.function_name, state.repository)
    state.functions = functions
    state.ds_repo_entity = ds_repo_entity


def load_repo_data(entity, function_name="create_scenario", repo_type="default"):
    data = data_storage.get(entity)
    _functions = list(data.function_name.unique())
    function_name = function_name if function_name in _functions else _functions[0]
    data = data[data.function_name == function_name]
    data["repo_type_entity_count"] = data.repo_type + "-" + data.entity_counts.astype(str)

    columns = ["datetime"]
    columns.extend(data["repo_type_entity_count"].unique())
    display_data = pd.DataFrame(columns=columns)

    for _, row in data.iterrows():
        if row["datetime"] in display_data["datetime"].unique():
            display_data.loc[display_data["datetime"] == row["datetime"], row["repo_type_entity_count"]] = row[
                "time_elapsed"
            ]
        else:
            new_row = {repo_type: None for repo_type in data["repo_type"].unique()}
            new_row["datetime"] = row["datetime"]
            new_row[row["repo_type_entity_count"]] = row["time_elapsed"]
            display_data = display_data.append([new_row], ignore_index=True)
    return display_data, _functions


# initial values
selected_dn_type = "json"
selected_exposed_type = "without_custom_encoder"
selected_function_name = "read_data_node"

data = data_storage.get("json")
display_data = convert_data_to_display(data, "read_data_node")
col_to_lines = {
    "csv": "y[1]=pandas|y[2]=Row|y[3]=numpy|y[4]=modin",
    "excel": "y[1]=pandas|y[2]=Row|y[3]=numpy|y[4]=modin",
    "pickle": "y[1]=list_dict|y[2]=list_object",
    "json": "y[1]=with_custom_encoder|y[2]=without_custom_encoder",
}

root_page = "<|navbar|>"

dn_report_page = """
<center><h1>Taipy core Data Node performance report</h1></center>

##Select data node type:
<center>
<|{selected_dn_type}|toggle|lov=csv;excel;json;pickle|>
</center>
<|layout|columns=1|
<|part|render=True|partial={partial}|>
|>
"""


repository = "default"
entities = ["scenario", "sequence", "task", "data_node"]
entity = "scenario"
function_name = "create_scenario"
ds_repo_entity, functions = load_repo_data(entity)
repo_report_page = """
<center><h1>Taipy core Repository performance report</h1></center>

## Select entity:
<center>
<|{entity}|toggle|lov=scenario;sequence;task;data_node|on_change=on_change_entity|>
</center>

##Select function:
<center>
<|{function_name}|toggle|lov={functions}|on_change=on_change_entity|>
</center>
<|{ds_repo_entity}|chart|type=line|x=datetime|y[1]=default-10|y[2]=sql-10|y[3]=mongo-10|y[4]=default-100|y[5]=sql-100|y[6]=mongo-100|height=200%|>

|>
"""


pages = {"/": root_page, "dn-perf": dn_report_page, "repository-perf": repo_report_page}
gui = Gui(pages=pages)
partial = gui.add_partial(create_partial_content(display_data=display_data))

if __name__ == "__main__":
    gui.run()
