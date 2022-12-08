import os
from pathlib import Path

from taipy.config import Config
import taipy as tp

class PerfBenchmarkAbstract:
    
    BENCHMARK_REPORT_FILE_NAME = None
    BENCHMARK_FOLDER_NAME = "benchmark_results"

    def __init__(self, report_path: str = None, folder_path: str = None):
        Config.unblock_update()
        Config.configure_global_app(clean_entities_enabled=True)
        
        self.folder_path = folder_path if folder_path else Path(__file__).parent.resolve()

        benchmark_folder_path = os.path.join(
            self.folder_path, 
            ("" if os.getenv("TAIPY_PERFORMANCE_BENCHMARK") else "sample_") + self.BENCHMARK_FOLDER_NAME
        )
        self.report_path = report_path if report_path else os.path.join(benchmark_folder_path, self.BENCHMARK_REPORT_FILE_NAME)
        
        Path(str(benchmark_folder_path)).mkdir(parents=True, exist_ok=True)

    def __del__(self):
        tp.clean_all_entities()

    def run(self):
        ...
