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

from taipy._cli._base_cli import _CLI


def clean_subparser():
    if getattr(_CLI._parser, "_subparsers", None):
        # Loop over all subparsers to find the one that has nested-subparsers and positional arguments
        for choice in _CLI._parser._subparsers._group_actions[0].choices.values():

            # Remove nested _subparsers
            choice._subparsers = None

            # Remove positional arguments
            # The "==SUPPRESS==" is a hack to identify nested-subparsers as positional arguments
            to_remove = ["application_main_file", "==SUPPRESS=="]

            actions = choice._actions.copy()
            for action in actions:
                opts = action.option_strings
                if (opts and opts[0] in to_remove) or action.dest in to_remove:
                    choice._remove_action(action)

            for argument_group in choice._action_groups:
                for group_action in argument_group._group_actions:
                    opts = group_action.option_strings
                    if (opts and opts[0] in to_remove) or group_action.dest in to_remove:
                        argument_group._group_actions.remove(group_action)


def assert_true_after_time(assertion, msg=None, time=120):
    from datetime import datetime
    from time import sleep

    start = datetime.now()
    while (datetime.now() - start).seconds < time:
        print(f"waiting {(datetime.now() - start).seconds} seconds...", end="\r")
        try:
            if assertion():
                print(f"waiting {(datetime.now() - start).seconds} seconds...")
                return
        except BaseException as e:
            print("Raise : ", e)
            sleep(1)  # Limit CPU usage
            continue
    print(f"waiting {(datetime.now() - start).seconds} seconds...")
    if msg:
        print(msg)
    assert assertion()
