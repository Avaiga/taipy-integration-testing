import os
from pathlib import Path

from csv_perf_benchmark import CSVPerfBenchmark
from excel_perf_benchmark import ExcelPerfBenchmark
from pickle_perf_benchmark import PicklePerfBenchmark
from json_perf_benchmark import JsonPerfBenchmark

if __name__ == "__main__":
    parent_path = Path(__file__).parent.resolve()
    
    csv_report_path = os.path.join(parent_path, "benchmark_report_csv_data_node.csv")
    CSVPerfBenchmark(csv_report_path).run()

    excel_report_path = os.path.join(parent_path, "benchmark_report_excel_data_node.csv")
    ExcelPerfBenchmark(excel_report_path).run()
    
    pickle_report_path = os.path.join(parent_path, "benchmark_report_pickle_data_node.csv")
    PicklePerfBenchmark(pickle_report_path).run()
    
    json_report_path = os.path.join(parent_path, "benchmark_report_json_data_node.csv")
    JsonPerfBenchmark(json_report_path).run()