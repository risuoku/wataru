import re
import shlex
import random
import time
import subprocess
import wataru.exceptions as wtex
from wataru.logging import getLogger

logger = getLogger(__name__)


def snake2camel(s):
    return ''.join([a.capitalize() for a in s.split('_')]) # snake case -> camel case


def camel2snake(s):
    return re.sub("([A-Z])",lambda x:"_" + x.group(1).lower(), s)[1:] # camel case -> snake case


def do_console_command(s):
    pargs = shlex.split(s)
    with subprocess.Popen(pargs, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
        out, err = proc.communicate()
        if not proc.returncode == 0:
            raise wtex.ConsoleCommandFailed(err)
        logger.debug(out)


# Use the system PRNG if possible
try:
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    import warnings
    warnings.warn('A secure pseudo-random number generator is not available '
                  'on your system. Falling back to Mersenne Twister.')
    using_sysrandom = False

DEFAULT_ALLOWED_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
def get_random_string(length=12, allowed_chars=DEFAULT_ALLOWED_CHARS):
    """
    implementation inspired by Django
    """
    if not using_sysrandom:
        random.seed(
                    hashlib.sha256(
                        ("%s%s%s" % (
                            random.getstate(),
                            time.time(),
                            settings.SECRET_KEY)).encode('utf-8')
                    ).digest())
    return ''.join(random.choice(allowed_chars) for i in range(length))


def save_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content + '\n')
