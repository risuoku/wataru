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
import wataru.utils as utils
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
            re.search('$.*\.pyc^', s) is not None
        )
    ignore_files = [fn for fn in files if _ignore_pattern(fn)]
    return ignore_files


def materialize(scenario, scenario_path, mtpath):
    if not isinstance(scenario, Scenario):
        raise TypeError('`scenario` must be Scenario')
    os.makedirs(mtpath, exist_ok=True)

    #本当はconfigがjson serializableになってるのが正しいがまだ出来ないので暫定でこうする
    #material_id = utils.get_hash(json.dumps(scenario.config))
    material_id = utils.get_hash(datetime.datetime.now().isoformat())

    spath = os.path.join(mtpath, material_id)
    if os.path.isfile(spath):
        raise ValueError('{} already exists.'.format(material_id))

    try:
        # create and sync scenario_dir
        shutil.copytree(scenario_path, spath, ignore=ignore_for_copytree)
        logger.debug('scenario {} materialized done.'.format(spath))

        # update materialized meta
        rosess = get_session()
        ms = rosess.query(ModelScenario).filter_by(name=scenario.name).first()
        with session_scope() as session:
            if ms is None:
                session.add(ModelScenario(name=scenario.name))
                ms = session.query(ModelScenario).filter_by(name=scenario.name).first()
            session.add(ModelMaterial(scenario_id=ms.id, id=material_id))
        logger.debug('meta information materialized done.')

    except:
        shutil.rmtree(spath)
        logger.debug('remove materialized scenario {} done.'.format(spath))
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
