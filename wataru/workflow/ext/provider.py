from wataru.workflow.provider import (
    Provider,
    provider_generator,
    default_name_function,
)
from wataru.logging import getLogger
import collections
import importlib
import os

logger = getLogger(__name__)


# for ChainerProvider

try:
    import chainer
    class ChainerProvider(Provider):
        def get_model_name(self, tr_name):
            return '{}_{}'.format(self.__class__.__name__, tr_name)

        def build(self, with_saved = False):
            train_data, test_data = self.to_chainerdataset()
            for idx, trc in enumerate(self._config['trainers']):
                entry_mod_name, entry_func_name = tuple(trc['entry'].split(':'))
                tr_name = trc.get('name', 'trainer{}'.format(idx))
                _get_trainer_func = getattr(importlib.import_module('.' + entry_mod_name, self._package_name), entry_func_name)
                trainer = _get_trainer_func(train_data, test_data)
                if with_saved and self._material_location is not None:
                    chainer.serializers.load_npz(os.path.join(self._material_location, self.get_model_name(tr_name) + '.npz'), trainer)
                    logger.debug('load from saved.')
                self._trainers[tr_name] = trainer
    
        def run(self, with_save = True):
            for name, trainer in self._trainers.items():
                logger.debug('trainer {} run start.'.format(name))
                trainer.run()
                if with_save and self._material_location is not None:
                    chainer.serializers.save_npz(os.path.join(self._material_location, self.get_model_name(name) + '.npz'), trainer)
                logger.debug('trainer {} run done.'.format(name))
            return self
    
        def to_chainerdataset(self):
            raise NotImplementedError()

    
    def chainer_provider_generator(iterator, f, name_function = default_name_function):
        if not isinstance(iterator, collections.Iterable):
            raise TypeError('`iterator` must be iterable.')
        if not f.__name__ == 'to_chainerdataset':
            raise ValueError('invalid function name .. {}'.format(f.__name__))
        chainer_iterator = [{'to_chainerdataset': ite} for ite in iterator]
        return provider_generator(chainer_iterator, [f], name_function = name_function, parent_class = ChainerProvider)

except ImportError:
    logger.debug('import ChainerProvider failed!')
