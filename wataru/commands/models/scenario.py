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
        try:
            smod = importlib.import_module('.'.join([settings_general['scenarios_module_name'], namespace.scenarioname, settings_general['scenario_entry_module_name']]))
            sobj = getattr(smod, settings_general['scenario_entry_function_name'])()
            sobj.set('package_name', '.'.join([settings_general['scenarios_module_name'], namespace.scenarioname]))
            sobj.build()
        except:
            logger.error('instanize scenario object failed!')
            raise
        wfproject.materialize(
            namespace.scenarioname,
            os.path.join(settings_general['project_base_path'], settings_general['scenarios_module_name'], namespace.scenarioname),
            settings_general['materialized_dir']
        )


class Ls(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')

    def execute(self, namespace):
        settings_general = self.settings['general']
        _list = wfproject.list_scenarios()
        pprint.pprint([o.name for o in _list])


class Sync(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')

    def execute(self, namespace):
        settings_general = self.settings['general']
        wfproject.create_scenarios(settings_general['project_base_path'], settings_general['scenarios_module_name'])


class Rm(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')
        parser.add_argument('-t', action='store', dest='target', default=None)
        parser.add_argument('--all', action='store_true', dest='all')

    def execute(self, namespace):
        if (not namespace.all) and namespace.target is None:
            raise Exception('target or all must be activated!')

        rosess = wfstate.get_session()
        if namespace.all:
            target_names = [t.name for t in rosess.query(wfstate.Scenario).all()]
        else:
            target_names = namespace.target.split(',')

        settings_general = self.settings['general']
        wfproject.remove_scenarios(target_names, settings_general['materialized_dir'])
