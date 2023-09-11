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

from taipy import Config, Core, Gui

if __name__ == "__main__":
    core = Core()
    core.run()

    gui = Gui()
    gui._config._handle_argparse()

    print(f"Config.core.version_number: {Config.core.version_number}")
    print(f"Config.core.mode: {Config.core.mode}")
    print(f"Config.core.force: {Config.core.force}")
    print(f"Config.gui_config.host: {gui._config.config.get('host', None)}")
    print(f"Config.gui_config.port: {gui._config.config.get('port', None)}")
    print(f"Config.gui_config.debug: {gui._config.config.get('debug', None)}")
    print(f"Config.gui_config.use_reloader: {gui._config.config.get('use_reloader', None)}")
    print(f"Config.gui_config.ngrok_token: {gui._config.config.get('ngrok_token', None)}")
    print(f"Config.gui_config.webapp_path: {gui._config.config.get('webapp_path', None)}")
