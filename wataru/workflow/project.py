from wataru.workflow.scenario import Scenario
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
    #scenario_id = utils.get_hash(json.dumps(scenario.config))
    scenario_id = utils.get_hash(datetime.datetime.now().isoformat())

    spath = os.path.join(mtpath, scenario_id)
    if os.path.isfile(spath):
        raise ValueError('{} already exists.'.format(scenario_id))

    try:
        # create and sync scenario_dir
        shutil.copytree(scenario_path, spath, ignore=ignore_for_copytree)
        logger.debug('scenario {} materialized done.'.format(spath))

        # update materialized meta
        db_meta = {
            'name2id': {},
        }
        meta_file = os.path.join(mtpath, 'meta.pickle')
        if os.path.isfile(meta_file):
            with open(meta_file, 'rb') as f:
                db_meta = pickle.load(f)
        if scenario.name not in db_meta['name2id']:
            db_meta['name2id'][scenario.name] = []
        _now = datetime.datetime.now()
        db_meta['name2id'][scenario.name].append({
            'id': scenario_id,
            'created_at': _now,
            'updated_at': _now,
            'status': 'created',
        })
        with open(meta_file, 'wb') as f:
            pickle.dump(db_meta, f)
        logger.debug('meta information materialized done.')

    except:
        shutil.rmtree(spath)
        logger.debug('remove materialized scenario {} done.'.format(spath))
        raise 


def list_materials(scenario_name, mtpath):
    meta_file = os.path.join(mtpath, 'meta.pickle')
    if not os.path.isfile(meta_file):
        return []
    else:
        with open(meta_file, 'rb') as f:
            db_meta = pickle.load(f)
        name2id = db_meta['name2id']
        if scenario_name not in name2id:
            return []
        else:
            return name2id[scenario_name]


def list_scenarios(mtpath):
    meta_file = os.path.join(mtpath, 'meta.pickle')
    if not os.path.isfile(meta_file):
        return []
    else:
        with open(meta_file, 'rb') as f:
            db_meta = pickle.load(f)
        name2id = db_meta['name2id']
        return list(name2id.keys())
