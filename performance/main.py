import os
from pathlib import Path

from performance.csv_perf_tester import CSVPerfTester

if __name__ == "__main__":
    path = os.path.join(Path(__file__).parent.resolve(), "report_csv_data_node.csv")
    CSVPerfTester(path).run()
