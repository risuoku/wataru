from wataru.commands.models.base import CommandBase
from wataru.logging import getLogger
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
        # create scenario
        seggings_general = self.settings['general']
        _list = wfproject.list_materials(namespace.scenarioname, settings_general['materialized_dir'])
        pprint.pprint(sorted(_list, key=lambda x: x['updated_at'], reverse=True))


class Run(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')
        parser.add_argument('material_id', action='store')

    def execute(self, namespace):
        seggings_general = self.settings['general']
        wfscenario.run(namespace.material_id, settings_general)
