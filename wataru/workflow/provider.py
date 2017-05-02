from wataru.logging import getLogger
import sys

logger = getLogger(__name__)


class Provider:
    def __init__(self, config, data, package_name, material_location):
        self._config = config
        self._data = data
        self._package_name = package_name
        self._material_location = material_location
        self._trainers = {}

    def build(self):
        return self

    def run(self):
        for name, tr in self._trainers.items():
            logger.debug('trainer {} run start.'.format(name))
            logger.debug('trainer {} run done.'.format(name))
        return self

    @property
    def trainers(self):
        return self._trainers
    
    @property
    def data(self):
        return self._data
