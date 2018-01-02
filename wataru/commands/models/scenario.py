from wataru.commands.models.base import CommandBase
from wataru.logging import getLogger
import wataru.workflow.project as wfproject
import wataru.workflow.state as wfstate
import wataru.workflow.scenario as wfscenario
import wataru.workflow.operations as wfoperations

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
        material_id = wfproject.materialize(
            namespace.scenarioname,
            os.path.join(settings_general['project_base_path'], settings_general['scenarios_module_name'], namespace.scenarioname),
            settings_general['materialized_dir']
        )
        logger.info('material_id: {}'.format(material_id))
        self.material_id = material_id


class Train(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')
        parser.add_argument('--allow-completed', action='store_true', dest='allowcompleted', default=False)
        parser.add_argument('--materialize-enabled', action='store_true', dest='materialize_enabled', default=False)
        parser.add_argument('scenarioname', action='store')

    def execute(self, namespace):
        if namespace.materialize_enabled:
            cmd = Materialize()
            cmd.settings = self.settings
            cmd.execute(namespace)
            settings_general = self.settings['general']
            wfoperations.train(cmd.material_id, settings_general, namespace.allowcompleted)
        else:
            settings_general = self.settings['general']
            wfoperations.train_without_materialized(namespace.scenarioname, settings_general)


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
