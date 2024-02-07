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
from taipy import Submission
from taipy._cli._base_cli import _CLI
from taipy.logger._taipy_logger import _TaipyLogger


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


def assert_true_after_time(assertion, time=120, msg=None, **msg_params):
    from datetime import datetime
    from time import sleep

    start = datetime.now()
    while (datetime.now() - start).seconds < time:
        sleep(0.2)  # Limit CPU usage
        try:
            if assertion():
                return
        except BaseException as e:
            _TaipyLogger()._get_logger().error("Raise : ", e)
            continue
    if msg:
        _TaipyLogger()._get_logger().error(msg(**msg_params))
    assert assertion()


def message(submission: Submission, timeout=120):
    ms = "--------------------------------------------------------------------------------\n"
    ms += f"Submission status is {submission.submission_status} after {timeout} seconds.\n"
    ms += "                              --------------                                    \n"
    ms += "                               Job statuses                                     \n"
    for job in submission.jobs:
        ms += f"{job.id}: {job.status}\n"
    ms += "                              --------------                                    \n"
    ms += "                               Blocked jobs                                     \n"
    for job in submission._blocked_jobs:
        ms += f"{job.id}\n"
    ms += "                              --------------                                    \n"
    ms += "                               Running jobs                                     \n"
    for job in submission._running_jobs:
        ms += f"{job.id}\n"
    ms += "                              --------------                                    \n"
    ms += "                               Pending jobs                                     \n"
    for job in submission._pending_jobs:
        ms += f"{job.id}\n"
    ms += "--------------------------------------------------------------------------------\n"
    return ms
