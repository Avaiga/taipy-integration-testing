from taipy import Config


def mult_by_2(a):
    return a


def build_skipped_jobs_config():
    input_config = Config.configure_data_node(id="input_dn", default_data=2)
    intermediate_config = Config.configure_data_node(id="intermediate_dn")
    output_config = Config.configure_data_node(id="output_dn")
    task_config_1 = Config.configure_task("first", mult_by_2, input_config, intermediate_config, skippable=True)
    task_config_2 = Config.configure_task("second", mult_by_2, intermediate_config, output_config, skippable=True)
    scenario_config = Config.configure_scenario("scenario", task_configs=[task_config_1, task_config_2])
    return scenario_config
