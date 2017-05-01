from wataru.commands.models.base import CommandBase
from wataru.logging import getLogger
import wataru.workflow.utils as wfutils
import wataru.workflow.project as wfproject

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
        settings = wfutils.get_setttings_from_configpath(os.path.abspath(namespace.configpath))

        # create scenario
        if settings['project_base_path'] not in sys.path:
            sys.path.append(settings['project_base_path'])
        smod = importlib.import_module('.'.join([settings['scenarios_module_name'], namespace.scenarioname, settings['scenario_entry_module_name']]))
        sobj = getattr(smod, settings['scenario_entry_function_name'])()
        wfproject.materialize(sobj, os.path.join(settings['project_base_path'], settings['scenarios_module_name'], namespace.scenarioname), settings['materialized_dir'])


class Ls(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')

    def execute(self, namespace):
        settings = wfutils.get_setttings_from_configpath(os.path.abspath(namespace.configpath))

        # create scenario
        if settings['project_base_path'] not in sys.path:
            sys.path.append(settings['project_base_path'])
        _list = wfproject.list_scenarios(settings['materialized_dir'])
        pprint.pprint(_list)
