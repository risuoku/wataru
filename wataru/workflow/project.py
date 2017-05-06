from wataru.workflow.scenario import Scenario
from wataru.workflow.state import (
    Scenario as ModelScenario,
    Material as ModelMaterial,
    session_scope,
    get_session,
)
import os
import json
import shutil
import itertools
import wataru.utils as utils
import wataru.workflow.utils as wfutils
from wataru.logging import getLogger
import datetime
import pickle
import copy
import re

logger = getLogger(__name__)


def ignore_for_copytree(d, files):
    def _ignore_pattern(s):
        return (
            re.search('__pycache__', s) is not None or
            re.search('^.*\.pyc$', s) is not None
        )
    ignore_files = [fn for fn in files if _ignore_pattern(fn)]
    return ignore_files


def create_scenarios(base_path, scenario_module_name):
    scenarios_path = os.path.join(base_path, scenario_module_name)
    scenario_modules = [m for m in os.listdir(scenarios_path) if os.path.isdir(os.path.join(scenarios_path, m))]

    rosess = get_session()
    ms = rosess.query(ModelScenario).filter(ModelScenario.name.in_(scenario_modules))
    s_exist = [m.name for m in ms]
    valid_modules = [m for m in scenario_modules if m not in s_exist]

    # create scenarios
    if len(valid_modules) > 0:
        with session_scope() as session:
            session.add_all([ModelScenario(name=m) for m in valid_modules])
    else:
        logger.debug('all scenarios seem to be already created.')


def materialize(scenario_name, scenario_path, mtpath):
    os.makedirs(mtpath, exist_ok=True)

    material_id = utils.get_hash(datetime.datetime.now().isoformat())

    spath = os.path.join(mtpath, material_id)
    if os.path.isfile(spath):
        raise ValueError('{} already exists.'.format(material_id))

    try:
        # update materialized meta
        rosess = get_session()
        ms = rosess.query(ModelScenario).filter_by(name=scenario_name).first()
        with session_scope() as session:
            if ms is None:
                session.add(ModelScenario(name=scenario_name))
                ms = session.query(ModelScenario).filter_by(name=scenario_name).first()
            session.add(ModelMaterial(scenario_id=ms.id, id=material_id, tag=material_id))
            logger.debug('meta information materialized done.')

            # create and sync scenario_dir
            shutil.copytree(scenario_path, spath, ignore=ignore_for_copytree)
            logger.debug('scenario {} materialized done.'.format(spath))
        return material_id

    except:
        shutil.rmtree(spath)
        logger.debug('remove materialized scenario {} done.'.format(spath))
        raise 


def remove_scenarios(scenario_names, mtpath):
    rosess = get_session()
    targets = rosess.query(ModelScenario).filter(ModelScenario.name.in_(scenario_names))
    material_ids = list(itertools.chain.from_iterable([[mm.id for mm in ms.materials] for ms in targets]))

    with session_scope() as session:
        # remove materials
        remove_materials(material_ids, mtpath)

        # delete from db 
        session.query(ModelScenario).filter(ModelScenario.name.in_(scenario_names)).delete(synchronize_session='fetch')


def remove_materials(material_ids_or_tags, mtpath):
    material_ids = wfutils.get_material_id(material_ids_or_tags)
    material_paths = [os.path.join(mtpath, mid) for mid in material_ids]

    try:
        with session_scope() as session:
            # delete from db
            session.query(ModelMaterial).filter(ModelMaterial.id.in_(material_ids)).delete(synchronize_session='fetch')
            logger.debug('remove from db done.')

            # delete from material path
            for t in material_paths:
                if os.path.isdir(t):
                    shutil.rmtree(t)
            logger.debug('remove from material path done.')
    except:
        logger.error('remove materials failed! remove from db rollbacked .. but files may be partially deleted.')
        raise


def list_materials(scenario_name):
    rosess = get_session()
    ms = rosess.query(ModelScenario).filter_by(name=scenario_name).first()
    if ms is None:
        return []
    else:
        return ms.materials


def list_scenarios():
    rosess = get_session()
    ms = rosess.query(ModelScenario).all()
    return ms
