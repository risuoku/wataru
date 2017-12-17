import sys
import re
import copy
from wataru.logging import getLogger
from .parser import WataruArgumentParser

logger = getLogger(__name__)
parser = WataruArgumentParser().build()


def is_help(s):
    return s in ('-h', '--help')


def deprecated_execute_from_argument(argv = None):
    import wataru.commands.deprecated.parser as wp # lazy import
    argv = argv or sys.argv
    if not (isinstance(argv, list) or len(argv) > 0):
        raise ValueError()
    argv_core = argv[1:]
    subcmd = None
    if len(argv_core) == 0:
        argv_core = ['--help']
    elif is_help(argv_core[0]):
        argv_core = ['--help']
    else:
        subcmd = argv_core[0]
        
    parser = wp.get()
    cmd_obj = parser.parse_and_create(argv_core, subcmd) # exit if help or invalid

    try:
        cmd_obj.execute()
        logger.info('{} normally completed.'.format(subcmd))
    except Exception as e:
        logger.error(e, exc_info=True)
        sys.exit(1)


def execute_from_argument(argv = None):
    rawargs = sys.argv[1:]
    if len(rawargs) == 0:
        rawargs = ['--help']

    namespace = parser.parse_args(rawargs)
    subparsers = [(re.sub('subparser__', '', k), v) for k, v in vars(namespace).items() if re.search('^subparser__.+$', k) is not None and v is not None]
    if len(subparsers) > 0:
        longest, method = sorted(subparsers, key=lambda x: x[0], reverse=True)[0]
        cmd_stack = longest.split('_')[1:]
        cmd_stack.append(method)
        cmd = copy.copy(models.tree)
        for k in cmd_stack:
            cmd = cmd[k]
        if isinstance(cmd, dict):
            parser.parse_args(rawargs + ['--help'])
        try:
            cmd.execute_all(namespace)
            logger.debug('{} normally completed.'.format(' '.join(cmd_stack)))
        except Exception as e:
            logger.error(e, exc_info=True)
            sys.exit(1)
    else:
        pass
