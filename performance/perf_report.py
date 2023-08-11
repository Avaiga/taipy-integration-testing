import pandas as pd
from taipy import Gui


def on_change(state, var_name, var_value):
    state, function_names = generate_display_data(state)
    if var_name == "selected_dn_type":
        state.partial.update_content(state, create_partial_content(display_data=display_data, function_names=function_names, state=state))

def create_partial_content(display_data=None, function_names=None, state=None):
    if state:
        col_to_line = col_to_lines[state.selected_dn_type]
    else:
        col_to_line = col_to_lines['json']

    if function_names:
        function_names = ';'.join(function_names)
    else:
        function_names = 'read_data_node;write_data_node;submit_pipeline;submit_scenario'

    partial_content = '''##Select function name: <center><|{selected_function_name}|toggle|lov='''+function_names+'''|></center><|{display_data}|chart|mode=line|x=datetime|'''+col_to_line+'''|>'''
    return partial_content

def generate_display_data(state):
    data = pd.read_csv(f"performance/benchmark_results/{state.selected_dn_type.lower()}_data_node_benchmark_report.csv", header=0)
    state.display_data = convert_data_to_display(data, state.selected_function_name)
    return state, data['function_name'].unique().tolist()

def convert_data_to_display(data, selected_function_name):
    data = data[data['function_name'] == selected_function_name]
    columns = ['datetime']
    columns.extend(data['exposed_type'].unique())
    display_data = pd.DataFrame(columns=columns)

    for _, row in data.iterrows():
        if row['datetime'] in display_data['datetime'].unique():
            display_data.loc[display_data['datetime'] == row['datetime'], row['exposed_type']] = row['time_elapsed']
        else:
            new_row = {exposed_type: None for exposed_type in data['exposed_type'].unique()}
            new_row['datetime'] = row['datetime']
            new_row[row['exposed_type']] = row['time_elapsed']
            display_data = display_data.append([new_row], ignore_index=True)
    return display_data

def on_change_entity(state):
    _entity = state.entity
    ds_repo_entity, functions = load_repo_data(_entity, state.function_name, state.repository)
    state.functions = functions
    state.ds_repo_entity = ds_repo_entity

def load_repo_data(entity, function_name="create_scenario", repo_type="default"):
    data = pd.read_csv(
        f"performance/benchmark_results/{entity}_benchmark_report.csv", header=0
    )
    _functions = list(data.function_name.unique())
    function_name = function_name if function_name in _functions else _functions[0]
    data = data[data.function_name == function_name]
    data["repo_type_entity_count"] = data.repo_type + "-" + data.entity_counts.astype(str)

    columns = ['datetime']
    columns.extend(data['repo_type_entity_count'].unique())
    display_data = pd.DataFrame(columns=columns)

    for _, row in data.iterrows():
        if row['datetime'] in display_data['datetime'].unique():
            display_data.loc[display_data['datetime'] == row['datetime'], row['repo_type_entity_count']] = row['time_elapsed']
        else:
            new_row = {repo_type: None for repo_type in data['repo_type'].unique()}
            new_row['datetime'] = row['datetime']
            new_row[row['repo_type_entity_count']] = row['time_elapsed']
            display_data = display_data.append([new_row], ignore_index=True)
    return display_data, _functions

#initial values
selected_dn_type = "json"
selected_exposed_type = "without_custom_encoder"
selected_function_name = "read_data_node"

data = pd.read_csv("performance/benchmark_results/json_data_node_benchmark_report.csv", header=0)
display_data = convert_data_to_display(data, 'read_data_node')
col_to_lines = {
    'csv': 'y[1]=pandas|y[2]=Row|y[3]=numpy|y[4]=modin',
    'excel': 'y[1]=pandas|y[2]=Row|y[3]=numpy|y[4]=modin',
    'pickle': 'y[1]=list_dict|y[2]=list_object',
    'json': 'y[1]=with_custom_encoder|y[2]=without_custom_encoder',
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
entities = ["scenario", "pipeline", "task", "data_node"]
entity = "scenario"
function_name = "create_scenario"
ds_repo_entity, functions = load_repo_data(entity)
repo_report_page = """
<center><h1>Taipy core Repository performance report</h1></center>

## Select entity:
<center>
<|{entity}|toggle|lov=scenario;pipeline;task;data_node|on_change=on_change_entity|>
</center>

##Select function:
<center>
<|{function_name}|toggle|lov={functions}|on_change=on_change_entity|>
</center>
<|{ds_repo_entity}|chart|type=line|x=datetime|y[1]=default-10|y[2]=sql-10|y[3]=mongo-10|y[4]=default-100|y[5]=sql-100|y[6]=mongo-100|height=200%|>

|>
"""


pages = {
    '/': root_page,
    'dn-perf': dn_report_page,
    'repository-perf': repo_report_page
}
gui = Gui(pages=pages)
partial = gui.add_partial(create_partial_content(display_data=display_data))

if __name__ == "__main__":
    gui.run()

