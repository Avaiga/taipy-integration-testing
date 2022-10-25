import pytest
import os
import shutil


@pytest.fixture(autouse=True)
def cleanup_data():
    from time import sleep

    sleep(0.1)
    if os.path.exists(".data"):
        shutil.rmtree(".data", ignore_errors=True)
    if os.path.exists("test.db"):
        os.remove("test.db")
