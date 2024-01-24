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

import os
import shutil
from io import StringIO
from unittest.mock import patch

import pytest
from taipy._cli._scaffold_cli import _ScaffoldCLI
from taipy._entrypoint import _entrypoint

from tests.utils import clean_subparser


@pytest.fixture(autouse=True, scope="function")
def clean_templates():
    clean_subparser()

    yield

    if os.path.exists("foo_app"):
        shutil.rmtree("foo_app", ignore_errors=True)
    if os.path.exists("bar_app"):
        shutil.rmtree("bar_app", ignore_errors=True)


class TestTaipyCreateCommand:

    def test_default_template(self):
        assert os.path.exists(_ScaffoldCLI._TEMPLATE_MAP["default"])

        inputs = "\n".join(["foo_app", "main.py", "bar", "", "", ""])
        with pytest.raises(SystemExit) as error:
            with patch("sys.stdin", StringIO(f"{inputs}\n")):
                with patch("sys.argv", ["prog", "create"]):
                    _entrypoint()
        assert "foo_app" in os.listdir(os.getcwd())
        assert error.value.code == 0

        clean_subparser()

        inputs = "\n".join(["bar_app", "main.py", "bar", "", "", ""])
        with pytest.raises(SystemExit) as error:
            with patch("sys.stdin", StringIO(f"{inputs}\n")):
                with patch("sys.argv", ["prog", "create", "--template", "default"]):
                    _entrypoint()
        assert "bar_app" in os.listdir(os.getcwd())
        assert error.value.code == 0

    def test_scenario_management_template(self):
        assert os.path.exists(_ScaffoldCLI._TEMPLATE_MAP["scenario-management"])

        inputs = "\n".join(["foo_app", "main.py", "bar", ""])
        with pytest.raises(SystemExit) as error:
            with patch("sys.stdin", StringIO(f"{inputs}\n")):
                with patch("sys.argv", ["prog", "create", "--template", "scenario-management"]):
                    _entrypoint()
        assert "foo_app" in os.listdir(os.getcwd())
        assert error.value.code == 0

    def test_non_existing_template(self, capsys):
        with pytest.raises(SystemExit) as error:
            with patch("sys.argv", ["prog", "create", "--template", "non-existing-template"]):
                _entrypoint()

        assert error.value.code == 2

        _, err_msg = capsys.readouterr()
        assert "argument --template: invalid choice: 'non-existing-template' (choose from" in err_msg
