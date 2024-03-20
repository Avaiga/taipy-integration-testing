import logging
import openpyxl

import os
import pathlib
import platform
import shutil
import sys

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
