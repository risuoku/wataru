from wataru.commands.models.base import CommandBase
from wataru.logging import getLogger
import wataru.workflow.utils as wfutils
import wataru.workflow.scenario as wfscenario

import os
import sys

logger = getLogger(__name__)


class Materialized(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')
        parser.add_argument('materialized_id', action='store')

    def execute(self, namespace):
        settings = wfutils.get_setttings_from_configpath(os.path.abspath(namespace.configpath))

        # create scenario
        if settings['project_base_path'] not in sys.path:
            sys.path.append(settings['project_base_path'])
        wfscenario.run(namespace.materialized_id, settings)
