import subprocess
import shlex
import re


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
    if len(get_shellcmd_result('which nvidia-smi')) == 0:
        # NVIDIAのGPUが利用できない
        return None
    else:
        r = list(map(int, get_shellcmd_result('nvidia-smi --query-gpu=index --format=csv,noheader')))
        if len(r) == 0:
            return None
        else:
            return r[0]
