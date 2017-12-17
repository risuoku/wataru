from wataru.logging import getLogger
import wataru.workflow.utils as wfutils
import sys
import collections
import inspect

logger = getLogger(__name__)


class Provider:
    trainer_factory = []
    item = {}

    def __init__(self, data, package_name, material_location, material_status_completed):
        self._data = data
        self._package_name = package_name
        self._material_location = material_location
        self._material_status_completed = material_status_completed
        self._trainers = collections.OrderedDict()
        self._transformed_data = None

    def get_model_name(self, tr_name):
        return '{}_{}'.format(self.__class__.__name__, tr_name)

    def build(self):
        self.build_started()

        # transform
        self._transformed_data = self.transform()

        raw_trainer_factories = self.__class__.trainer_factory
        if not isinstance(raw_trainer_factories, list):
            raise TypeError('`raw_trainer_factories` must be list.')
        for rawtf in raw_trainer_factories:
            if inspect.isfunction(rawtf):
                # just provider
                tr = rawtf(self.transformed_data)
                self._trainers[self.get_model_name(getattr(tr, 'name', tr.__class__.__name__))] = tr
            else:
                raise TypeError('invalid type!')
        
        self.build_finished()
        return self
    
    def build_started(self):
        pass
    
    def build_finished(self):
        pass

    def run(self, with_save = True):
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

    @property
    def transformed_data(self):
        return self._transformed_data

    def transform(self):
        raise NotImplementedError()
