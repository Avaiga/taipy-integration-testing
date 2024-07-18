# Copyright 2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import logging
import os
import pathlib
import platform
import shutil
import sys

import openpyxl


def test_openpyxl():
    tmp_folder = pathlib.Path(__file__).parent.resolve() / "output_folder"
    os.makedirs(tmp_folder)
    tmp_path = tmp_folder / "output.xlsx"
    shutil.copy(pathlib.Path(__file__).parent.resolve() / "openpyxl_test.xlsx", tmp_path)

    excel_file = openpyxl.load_workbook(tmp_path)
    excel_file.close()
    if tmp_folder.exists():
        try:
            shutil.rmtree(tmp_folder)  # Raises an error
        except Exception as e:
            logging.info("-------------------------------")
            logging.info(f"{openpyxl.__version__=}")
            logging.info(f"{sys.version=}")
            logging.info(f"{sys.version_info=}")
            logging.info(f"{platform.platform()}")
            raise e
