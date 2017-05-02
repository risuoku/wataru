from wataru.workflow.provider import Provider
from wataru.logging import getLogger

logger = getLogger(__name__)


# for ChainerProvider

try:
    import chainer
    import importlib
    import os
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

except ImportError:
    pass
