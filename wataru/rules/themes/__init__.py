from wataru.logging import getLogger

import sys
import os
import os.path
import re
from importlib.machinery import SourceFileLoader
import wataru.settings as settings

import yaml

logger = getLogger(__name__)

DEFAULT_PATH = os.path.join(settings.WATARU_BASE_DIR_PATH, 'rules', 'themes', 'default')
DEFAULT_NAME = 'default'


def get_config(name, abspath):
    config = None
    files = os.listdir(abspath)
    if (name + '.yml') in files or (name + '.yaml') in files:
        cfile = name + '.yml'
        cfile = cfile if cfile in files else name + '.yaml'
        with open(os.path.join(abspath, cfile)) as f:
            config = yaml.load(f)
        logger.debug('used yaml')
    else:
        pyloader = SourceFileLoader(name, os.path.join(abspath, name + '.py'))
        pyloader.load_module()
        mod = sys.modules[name]
        config = getattr(mod, name)
        logger.debug('used dict')
    return config


def get_default_config():
    return get_config(
        DEFAULT_NAME,
        os.path.abspath(DEFAULT_PATH)
    )


def chain_update_dict(original, dest, key_stack = []):
    pointer = original
    target = dest
    for k in key_stack:
        pointer = pointer[k]
        target = target[k]
    if isinstance(target, dict):
        for k, v in target.items():
            chain_update_dict(original, dest, key_stack + [k])
    else:
        if isinstance(pointer, dict):
            raise ValueError('invalid value!')
        else:
            if len(key_stack) > 0:
                p2 = original
                for k in key_stack[:-1]:
                    p2 = p2[k]
                p2[key_stack[-1]] = target


class Theme:
    def __init__(self, path = None, name = None):
        self._name = name
        self._path = path
        self._config = None
        self._abs_tpldir = None

    def build(self):
        default_config = get_default_config()
        
        if self._path is not None:
            abspath = os.path.abspath(self._path)
            self._name = self._name or os.path.basename(abspath)
            self._abs_tpldir = os.path.join(abspath, 'templates')
            self._config = default_config
            chain_update_dict(self._config, get_config(self._name, abspath))
        else:
            self._abs_tpldir = os.path.join(os.path.abspath(DEFAULT_PATH), 'templates')
            self._config = default_config

        self._validate()
        return self
    
    @property
    def config(self):
        return self._config

    @property
    def abs_tpldir(self):
        return self._abs_tpldir

    @property
    def top_node(self):
        return self._config.get('body')

    @property
    def meta(self):
        return self._config.get('meta')

    def _validate(self):
        # self._config must be set
        if self._config is None:
            raise ValueError('invalid config status')

        # top node_type must be 'project'
        if not self.top_node['type'] == 'project':
            raise ValueError('invalid node type .. top node_type must be project')

    def update(self, d):
        if not isinstance(d, dict):
            raise TypeError('invalid type!')
        self._config = chain_update_dict(self._config, d)

    def update_project(self, key, value):
        _project = self.top_node
        _project.update({key: value})
        return self

    def update_meta(self, key, value):
        if self.meta is None:
            self._config.update({'meta': {}})
        self._config['meta'].update({key: value})
        return self


def get_default():
    return Theme().build()

def get(path):
    return Theme (
        path = path
    ).build()
