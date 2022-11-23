import os
from pathlib import Path

from csv_perf_benchmark import CSVPerfBenchmark
from excel_perf_benchmark import ExcelPerfBenchmark
from pickle_perf_benchmark import PicklePerfBenchmark
from json_perf_benchmark import JsonPerfBenchmark

if __name__ == "__main__":
    CSVPerfBenchmark().run()
    ExcelPerfBenchmark().run()
    PicklePerfBenchmark().run()
    JsonPerfBenchmark().run()