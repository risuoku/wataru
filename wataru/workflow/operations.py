from wataru.logging import getLogger
from wataru.workflow.state import (
    Material as ModelMaterial,
    session_scope,
    get_session,
)
import wataru.workflow.utils as wfutils

import os
import sys
import importlib
import pickle
import datetime
import collections

logger = getLogger(__name__)


def build_material(material_id, settings, load_enabled):
    target_dir = os.path.join(settings['materialized_dir'], material_id)
    if os.path.isdir(target_dir):
        sys.path.append(settings['materialized_dir'])
        smod = importlib.import_module(material_id + '.' + settings['scenario_entry_module_name'])
        # check status
        mm_all = get_session().query(ModelMaterial).filter_by(id=material_id)
        sobj = None
        if mm_all.count() > 0:
            mm = mm_all[0]
            sobj = getattr(smod, settings['scenario_entry_function_name'])(material_id, target_dir, mm.status).build_managers(load_enabled, True)
        else:
            raise Exception('unexpected error! .. material management system may be broken.')
        return sobj
    else:
        raise Exception('material not found!')


def train(material_id_or_tag, settings, allowcompleted):
    """ モデルを訓練する """
    material_id = wfutils.get_material_id(material_id_or_tag)
    mm = get_session().query(ModelMaterial).filter_by(id=material_id).first()
    if mm is None:
        raise Exception('material not found!')
    
    if mm.is_completed() and (not allowcompleted):
        raise Exception('already train completed.')

    sobj = build_material(material_id, settings, True)

    with session_scope() as session:
        # notify processing
        mm = session.query(ModelMaterial).filter_by(id=material_id).first()
        mm.status = ModelMaterial.Status.PROCESSING.value
        mm.updated_at = datetime.datetime.now()

    with session_scope() as session:
        # update meta
        mm = session.query(ModelMaterial).filter_by(id=material_id).first()
        mm.updated_at = datetime.datetime.now()
        mm.status = ModelMaterial.Status.COMPLETED.value

        # run
        sobj.train_all()
    logger.debug('train_all {} done.'.format(material_id))


def train_without_materialized(scenario_name, settings):
    """ materialize無しでモデルを訓練する """
    smod = importlib.import_module('{}.{}.{}'.format(
        settings['scenarios_module_name'],
        scenario_name,
        settings['scenario_entry_module_name'],
    ))
    sobj = getattr(smod, settings['scenario_entry_function_name'])(None, None, None).build_managers(True, False)
    sobj.train_all()
