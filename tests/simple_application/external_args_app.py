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

import argparse

from taipy import Config, Core, Gui

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", dest="mode", type=str, default="training")
    parser.add_argument("--force", type=str, default="no")
    parser.add_argument("--host", dest="host", type=str, default="user_default_host.com")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--non-conflict-arg", type=str, default="")

    core = Core()
    core.run()

    gui = Gui()
    gui._config._handle_argparse()

    user_args, _ = parser.parse_known_args()

    print(f"Config.core.mode: {Config.core.mode}")
    print(f"User provided mode: {user_args.mode}")
    print(f"Config.core.force: {Config.core.force}")
    print(f"User provided force: {user_args.force}")
    print(f"Config.gui_config.host: {gui._config.config.get('host', None)}")
    print(f"User provided host: {user_args.host}")
    print(f"Config.gui_config.port: {gui._config.config.get('port', None)}")
    print(f"User provided port: {user_args.port}")
    print(f"User provided non-conflict-arg: {user_args.non_conflict_arg}")
