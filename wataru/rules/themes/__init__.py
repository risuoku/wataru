from wataru.logging import getLogger

import sys
import os
import os.path
import re
from importlib.machinery import SourceFileLoader
import wataru.settings as settings

import yaml

logger = getLogger(__name__)


class Theme:
    def __init__(self, path, name = None):
        self._name = name
        self._path = path
        self._config = None
        self._abs_tpldir = None

    def build(self):
        abspath = os.path.abspath(self._path)
        self._name = self._name or os.path.basename(abspath)
        self._abs_tpldir = os.path.join(abspath, 'templates')
        files = os.listdir(abspath)
        config = None
        if (self._name + '.yml') in files or (self._name + '.yaml') in files:
            cfile = self._name + '.yml'
            cfile = cfile if cfile in files else self._name + '.yaml'
            with open(os.path.join(abspath, cfile)) as f:
                self._config = yaml.load(f)
            logger.debug('used yaml')
        else:
            pyloader = SourceFileLoader(self._name, os.path.join(abspath, self._name + '.py'))
            pyloader.load_module()
            mod = sys.modules[self._name]
            self._config = getattr(mod, self._name)
            logger.debug('used dict')

        return self
    
    @property
    def config(self):
        return self._config

    @property
    def abs_tpldir(self):
        return self._abs_tpldir


def get_default():
    return Theme (
        path = os.path.join(settings.WATARU_BASE_DIR_PATH, 'rules', 'themes', 'default'), 
        name = 'default'
    ).build()
