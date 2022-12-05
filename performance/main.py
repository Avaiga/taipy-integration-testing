from csv_perf_benchmark import CSVPerfBenchmark
from excel_perf_benchmark import ExcelPerfBenchmark
from pickle_perf_benchmark import PicklePerfBenchmark
from json_perf_benchmark import JsonPerfBenchmark

ROW_COUNTS = [10 ** 3, 10 ** 4]

if __name__ == "__main__":
    CSVPerfBenchmark(ROW_COUNTS).run()
    ExcelPerfBenchmark(ROW_COUNTS).run()
    PicklePerfBenchmark(ROW_COUNTS).run()
    JsonPerfBenchmark(ROW_COUNTS).run()
