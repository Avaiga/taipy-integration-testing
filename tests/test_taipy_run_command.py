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

from unittest.mock import patch

import pytest
from taipy._entrypoint import _entrypoint

from tests.utils import clean_subparser


@pytest.fixture(autouse=True, scope="function")
def clean_templates():
    clean_subparser()
    yield


def test_run_simple_taipy_app_without_taipy_args(capfd):
    with pytest.raises(SystemExit) as error:
        with patch("sys.argv", ["prog", "run", "tests/simple_application/no_external_args_app.py"]):
            _entrypoint()
    std_out, _ = capfd.readouterr()
    assert error.value.code == 0
    assert "Development mode: Clean all entities of version" in std_out

    assert "Config.core.version_number: " in std_out
    assert "Config.core.mode: development" in std_out
    assert "Config.core.force: False" in std_out
    assert "Config.gui_config.host: 127.0.0.1" in std_out
    assert "Config.gui_config.port: 5000" in std_out
    assert "Config.gui_config.debug: False" in std_out
    assert "Config.gui_config.use_reloader: False" in std_out
    assert "Config.gui_config.ngrok_token: " in std_out
    assert "Config.gui_config.webapp_path: None" in std_out


def test_run_simple_taipy_app_with_taipy_args(capfd):
    with pytest.raises(SystemExit):
        with patch(
            "sys.argv",
            [
                "prog",
                "run",
                "tests/simple_application/no_external_args_app.py",
                "--experiment",
                "1.0",
                "--force",
                "--host",
                "example.com",
                "--port",
                "5001",
                "--debug",
                "--use-reloader",
                "--ngrok-token",
                "1234567890",
                "--webapp-path",
                "path/webapp",
            ],
        ):
            _entrypoint()

    std_out, _ = capfd.readouterr()
    assert "Config.core.version_number: 1.0" in std_out
    assert "Config.core.mode: experiment" in std_out
    assert "Config.core.force: True" in std_out
    assert "Config.gui_config.host: example.com" in std_out
    assert "Config.gui_config.port: 5001" in std_out
    assert "Config.gui_config.debug: True" in std_out
    assert "Config.gui_config.use_reloader: True" in std_out
    assert "Config.gui_config.ngrok_token: 1234567890" in std_out
    assert "Config.gui_config.webapp_path: path/webapp" in std_out


def test_run_simple_taipy_app_with_taipy_and_external_args(capfd):
    with pytest.raises(SystemExit):
        with patch(
            "sys.argv",
            [
                "prog",
                "run",
                "tests/simple_application/external_args_app.py",
                "--experiment",
                "1.0",
                "--force",
                "--host",
                "example.com",
                "--port",
                "5001",
                "external-args",  # This is the keyword that separates external args from taipy args
                "--mode",
                "inference",
                "--force",
                "yes",
                "--host",
                "user_host.com",
                "--port",
                "8081",
                "--non-conflict-arg",
                "non-conflict-arg-value",
            ],
        ):
            _entrypoint()

    std_out, _ = capfd.readouterr()
    assert "Config.core.mode: experiment" in std_out
    assert "User provided mode: inference" in std_out
    assert "Config.core.force: True" in std_out
    assert "User provided force: yes" in std_out
    assert "Config.gui_config.host: example.com" in std_out
    assert "User provided host: user_host.com" in std_out
    assert "Config.gui_config.port: 5001" in std_out
    assert "User provided port: 8081" in std_out
    assert "User provided non-conflict-arg: non-conflict-arg-value" in std_out
