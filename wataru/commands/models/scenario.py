from wataru.commands.models.base import CommandBase
from wataru.logging import getLogger
import wataru.workflow.project as wfproject
import wataru.workflow.state as wfstate

import yaml
import os
import sys
import importlib
import pprint

logger = getLogger(__name__)


class Materialize(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')
        parser.add_argument('scenarioname', action='store')

    def execute(self, namespace):
        settings_general = self.settings['general']
        smod = importlib.import_module('.'.join([settings['scenarios_module_name'], namespace.scenarioname, settings_general['scenario_entry_module_name']]))
        sobj = getattr(smod, settings_general['scenario_entry_function_name'])()
        wfproject.materialize(
            sobj,
            os.path.join(settings_general['project_base_path'], settings_general['scenarios_module_name'], namespace.scenarioname),
            settings_general['materialized_dir']
        )


class Ls(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')

    def execute(self, namespace):
        settings_general = self.settings['general']
        _list = wfproject.list_scenarios(settings_general['materialized_dir'])
        pprint.pprint(_list)
