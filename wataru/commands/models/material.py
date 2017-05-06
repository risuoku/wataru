from wataru.commands.models.base import CommandBase
from wataru.logging import getLogger
import wataru.workflow.project as wfproject
import wataru.workflow.scenario as wfscenario
import wataru.workflow.inspector as wfinspector
import wataru.workflow.utils as wfutils

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
        settings_general = self.settings['general']
        _list = wfproject.list_materials(namespace.scenarioname)
        pprint.pprint([
            {
                'id': o.id,
                'tag': o.tag,
                'status': o.status,
                'created_at': o.created_at,
                'updated_at': o.updated_at,
            }
            for o in sorted(_list, key=lambda x: x.updated_at, reverse=True)
        ])


class Run(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')
        parser.add_argument('material_id', action='store')

    def execute(self, namespace):
        settings_general = self.settings['general']
        wfscenario.run(namespace.material_id, settings_general)


class Rm(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')
        parser.add_argument('-t', action='store', dest='target', default=None)

    def execute(self, namespace):
        if namespace.target is None:
            raise Exception('target_ids must be activated!')

        target_ids = namespace.target.split(',')

        settings_general = self.settings['general']
        wfproject.remove_materials(target_ids, settings_general['materialized_dir'])


class Inspect(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')
        parser.add_argument('material_id', action='store')

    def pre_execute(self, namespace):
        pass

    def execute(self, namespace):
        mat = wfinspector.get_material(namespace.material_id, namespace.configpath)
        material_id = wfutils.get_material_id(namespace.material_id)

        # scenarios
        result = {
            'material_id': material_id,
            'material_status': mat.material_status,
            'scenario': {
                'name': mat.name,
                'providers': [
                    {
                        'name': pname,
                        'items': p.item,
                        'trainers': [
                            {
                                'name': tr_name,
                            }
                            for tr_name, tr in p.trainers.items()
                        ]
                    }
                    for pname, p in mat.providers.items()
                ]
            }
        }
        from pprint import pprint
        pprint(result)
