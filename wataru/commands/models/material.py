from wataru.commands.models.base import CommandBase
from wataru.logging import getLogger
import wataru.workflow.utils as wfutils
import wataru.workflow.project as wfproject
import wataru.workflow.scenario as wfscenario

import os
import sys
import pprint

logger = getLogger(__name__)


class Ls(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')
        parser.add_argument('scenarioname', action='store')

    def execute(self, namespace):
        settings = wfutils.get_setttings_from_configpath(os.path.abspath(namespace.configpath))

        # create scenario
        if settings['project_base_path'] not in sys.path:
            sys.path.append(settings['project_base_path'])
        _list = wfproject.list_materials(namespace.scenarioname, settings['materialized_dir'])
        pprint.pprint(sorted(_list, key=lambda x: x['updated_at'], reverse=True))


class Run(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')
        parser.add_argument('material_id', action='store')

    def execute(self, namespace):
        settings = wfutils.get_setttings_from_configpath(os.path.abspath(namespace.configpath))

        # create scenario
        if settings['project_base_path'] not in sys.path:
            sys.path.append(settings['project_base_path'])
        wfscenario.run(namespace.material_id, settings)
