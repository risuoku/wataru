import subprocess
import shlex
import re
import os


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


def get_setttings_from_config(cnf, base_path):
    management_dir = os.path.join(base_path, cnf['management_dir'])
    storage_dir = os.path.join(management_dir, cnf['storage_dir'])
    scenario_entry_module_name, scenario_entry_function_name = tuple(cnf['scenario_entry_name'].split(':'))
    return {
        'project_base_path': base_path,
        'management_dir': management_dir,
        'storage_dir': storage_dir,
        'scenarios_module_name': cnf['scenarios_module_name'],
        'scenario_entry_module_name': scenario_entry_module_name,
        'scenario_entry_function_name': scenario_entry_function_name,
    }
