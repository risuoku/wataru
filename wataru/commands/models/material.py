from wataru.commands.models.base import CommandBase
from wataru.logging import getLogger
import wataru.workflow.project as wfproject
import wataru.workflow.scenario as wfscenario
import wataru.workflow.inspector as wfinspector
import wataru.workflow.utils as wfutils
import wataru.workflow.operations as wfoperations

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


class Train(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')
        parser.add_argument('--allow-completed', action='store_true', dest='allowcompleted', default=False)
        parser.add_argument('material_id', action='store')

    def execute(self, namespace):
        settings_general = self.settings['general']
        wfoperations.train(namespace.material_id, settings_general, namespace.allowcompleted)


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
                'managers': [
                    {
                        'name': mgrname,
                        'param': mgr.param,
                        'models': [
                            {
                                'name': mdlname,
                                'hashed_id': mdl.get_hashed_id(),
                                'param': mdl.param
                            }
                            for mdlname, mdl in mgr.models.items()
                        ]
                    }
                    for mgrname, mgr in mat.managers.items()
                ]
            }
        }
        from pprint import pprint
        pprint(result)
