import wataru.workflow.state as wfstate
import wataru.workflow.utils as wfutils
import wataru.workflow.operations as wfoperation

import os
import sys


def get_material(material_id_or_tag, load_enabled = False, configpath=''):
    # prepare settings
    settings = wfutils.get_setttings_from_configpath(os.path.abspath(configpath))

    # setup PYTHONPATH
    if settings['general']['project_base_path'] not in sys.path:
        sys.path.append(settings['general']['project_base_path'])
    sys.path.append(settings['general']['materialized_dir'])

    # setup db
    wfstate.setup(settings['db'])

    material_id = wfutils.get_material_id(material_id_or_tag)

    return wfoperation.build_material(material_id, settings['general'], load_enabled)
