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
import abc
import os
from pathlib import Path
from typing import Optional
from taipy.logger._taipy_logger import _TaipyLogger
import taipy as tp
from taipy.config import Config

from _blob_manager import _BlobManager

class PerfBenchmarkAbstract:

    logger = _TaipyLogger._get_logger()

    BENCHMARK_REPORT_FILE_NAME: Optional[str]
    BENCHMARK_FOLDER_NAME: str = "benchmark_results"

    def __init__(self, report_path: str = None):
        Config.unblock_update()
        Config.configure_global_app(clean_entities_enabled=True)

        self.folder_path: Path = Path(__file__).parent.resolve()

        benchmark_folder_path: str = os.path.join(self.folder_path, self.BENCHMARK_FOLDER_NAME)
        self.report_path: str = (
            report_path if report_path else os.path.join(benchmark_folder_path, self.BENCHMARK_REPORT_FILE_NAME)  # type: ignore
        )

        Path(str(benchmark_folder_path)).mkdir(parents=True, exist_ok=True)
        
        if self.__is_prod:
            _BlobManager.download_file(self.BENCHMARK_REPORT_FILE_NAME, self.report_path)

    @property
    def __is_prod(self):
        return os.getenv("TAIPY_PERFORMANCE_BENCHMARK") == "0"

    def __del__(self):
        tp.clean_all_entities()
        if self.__is_prod:
            _BlobManager.upload_file(self.BENCHMARK_REPORT_FILE_NAME, self.report_path)

    def run(self):
        ...

    @property
    def BENCHMARK_NAME(self):
        raise NotImplementedError

    def log_header(self):
        self.logger.info("----------------------------------------------")
        self.logger.info("---  " + self.BENCHMARK_NAME.center(36) + "  ---")
        self.logger.info("----------------------------------------------")
