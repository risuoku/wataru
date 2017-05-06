import subprocess
import shlex
import re
import os
import sys
import yaml


class ConsoleCommand:
    def __init__(self, s):
        self._raw_string = s
        self._stdout = None
        self._stderr = None
    
    def execute(self):
        pargs = shlex.split(self._raw_string)
        with subprocess.Popen(pargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            self._stdout, self._stderr = proc.communicate()
        return self
    
    def get_stdout(self):
        return [s for s in self._stdout.decode('utf8').split('\n') if not s == '']


def get_shellcmd_result(s):
    return ConsoleCommand(s).execute().get_stdout()


def get_available_device_id():
    """ memory使用量の最も小さいGPU idを返す """
    if len(get_shellcmd_result('which nvidia-smi')) == 0:
        # NVIDIAのGPUが利用できない
        return None
    else:
        r = get_shellcmd_result('nvidia-smi --query-gpu=index,memory.used --format=csv,noheader')
        if len(r) == 0:
            return None
        else:
            def extract_idx_and_usedmemory(x):
                g = re.search('^([0-9]+),(\s+)?([0-9]+)(\s+)?MiB$', x).groups()
                return int(g[0]), int(g[2]) # 0: gpu index, 2: used memory
            sorted_gpus = sorted(map(extract_idx_and_usedmemory, r), key=lambda x: x[1])
            return sorted_gpus[0][0]


def get_setttings_from_configpath(configpath):
    config = None
    config_filepath = os.path.join(configpath, 'config.yml')
    with open(config_filepath) as f:
        config = yaml.load(f)

    # general settings
    config_general = config['general']
    management_dir = os.path.join(configpath, config_general['management_dir'])
    storage_dir = os.path.join(management_dir, config_general['storage_dir'])
    materialized_dir = os.path.join(storage_dir, config_general['materialized_name'])
    scenario_entry_module_name, scenario_entry_function_name = tuple(config_general['scenario_entry_name'].split(':'))
    
    # db settings
    config_db = config['db']
    if not config_db['vendor'] == 'sqlite':
        raise Exception('{} is unsupported'.format(config_db['vendor']))
    db_uri = '{}:///{}'.format(config_db['vendor'], os.path.join(storage_dir, config_db['dbname']))

    return {
        'general': {
            'project_base_path': configpath,
            'management_dir': management_dir,
            'storage_dir': storage_dir,
            'materialized_dir': materialized_dir,
            'scenarios_module_name': config_general['scenarios_module_name'],
            'scenario_entry_module_name': scenario_entry_module_name,
            'scenario_entry_function_name': scenario_entry_function_name,
        },
        'db': {
            'uri': db_uri,
        },
    }


class param:
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    @property
    def item(self):
        return self._args, self._kwargs

    def __repr__(self):
        return str(self.item)


def get_material_id(material_ids_or_tags):
    from .state import Material, get_session
    rosess = get_session()
    if isinstance(material_ids_or_tags, list):
        targets_by_tag = rosess.query(Material).filter(Material.tag.in_(material_ids_or_tags))
        targets_by_id = rosess.query(Material).filter(Material.id.in_(material_ids_or_tags))
        return list(set([t.id for t in targets_by_tag]) | set([t.id for t in targets_by_id]))
    elif isinstance(material_ids_or_tags, str):
        target_by_tag = rosess.query(Material).filter_by(tag=material_ids_or_tags).first()
        target_by_id = rosess.query(Material).filter_by(id=material_ids_or_tags).first()
        if target_by_tag is None and target_by_id is None:
            raise ValueError('target material not found.')
        if target_by_tag is not None and target_by_id is not None and target_by_tag.id !=  target_by_id.id:
            raise Exception('unknown status.')
        target = target_by_tag or target_by_id
        return target.id
    else:
        raise TypeError('invalid type. {}'.format(type(material_ids_or_tags)))
