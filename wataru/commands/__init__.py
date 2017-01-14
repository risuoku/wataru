import sys
from wataru.logging import getLogger

logger = getLogger(__name__)

def is_help(s):
    return s in ('-h', '--help')

def execute_from_argument(argv = None):
    import wataru.commands.parser as wp # lazy import
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
