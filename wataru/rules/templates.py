import jinja2
import wataru.settings as settings
import sys

_env = None
_abspath = None

def setenv(abspath):
    me = sys.modules[__name__]
    if me._env is None:
        me._env = jinja2.Environment (
            loader = jinja2.FileSystemLoader(abspath, encoding='utf-8')
        )
        me._abspath = abspath

def get(path):
    return _env.get_template(path)

def get_template_abspath():
    if _abspath is None:
        raise ValueError('template abspath not set')
    else:
        return _abspath
