import wataru.workflow.utils as wfutils
import wataru.workflow.state as wfstate
import os
import sys


class CommandBase:
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')

    def pre_execute(self, namespace):
        # prepare settings
        self.settings = wfutils.get_setttings_from_configpath(os.path.abspath(namespace.configpath))

        # setup PYTHONPATH
        if self.settings['general']['project_base_path'] not in sys.path:
            sys.path.append(self.settings['general']['project_base_path'])

        # setup db
        wfstate.setup(self.settings['db'])

    def execute(self, namespace):
        raise NotImplementedError()

    def execute_all(self, namespace):
        self.pre_execute(namespace)
        self.execute(namespace)
