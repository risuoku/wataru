import subprocess
import shlex
import re
import os
import sys
import yaml
from contextlib import contextmanager

import wataru.workflow.state as wfstate
import wataru.workflow.scenario as wfscenario


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


@contextmanager
def material_scope(material_id, configpath=''):
    # prepare settings
    settings = get_setttings_from_configpath(os.path.abspath(configpath))

    # setup PYTHONPATH
    if settings['general']['project_base_path'] not in sys.path:
        sys.path.append(settings['general']['project_base_path'])
    sys.path.append(settings['general']['materialized_dir'])

    # setup db
    wfstate.setup(settings['db'])

    yield wfscenario.build(material_id, settings['general'], need_not_completed = False)
