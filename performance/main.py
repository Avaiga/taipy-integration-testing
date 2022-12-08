from csv_perf_benchmark import CSVPerfBenchmark
from excel_perf_benchmark import ExcelPerfBenchmark
from pickle_perf_benchmark import PicklePerfBenchmark
from json_perf_benchmark import JsonPerfBenchmark
from scenario_perf_benchmark import ScenarioPerfBenchmark
from end_to_end_scenario_creation_perf_benchmark import EndToEndScenarioCreationPerfBenchmark

ROW_COUNTS = [10 ** 3, 10 ** 4]
ENTITY_COUNTS = [10 ** 2, 10 ** 3]
SCENARIO_COUNTS = [10 ** 1, 10 ** 2]

if __name__ == "__main__":
    CSVPerfBenchmark(ROW_COUNTS).run()
    ExcelPerfBenchmark(ROW_COUNTS).run()
    PicklePerfBenchmark(ROW_COUNTS).run()
    JsonPerfBenchmark(ROW_COUNTS).run()
    ScenarioPerfBenchmark(ENTITY_COUNTS).run()
    EndToEndScenarioCreationPerfBenchmark(SCENARIO_COUNTS).run()