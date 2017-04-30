from wataru.commands.models.base import CommandBase
from wataru.logging import getLogger
import wataru.workflow.utils as wfutils
import wataru.workflow.project as wfproject

import os
import sys
import pprint

logger = getLogger(__name__)


class Scenario(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')
        parser.add_argument('scenarioname', action='store')

    def execute(self, namespace):
        settings = wfutils.get_setttings_from_configpath(os.path.abspath(namespace.configpath))

        # create scenario
        if settings['project_base_path'] not in sys.path:
            sys.path.append(settings['project_base_path'])
        _list = wfproject.list_materialized(namespace.scenarioname, settings['materialized_dir'])
        pprint.pprint(sorted(_list, key=lambda x: x['updated_at'], reverse=True))
