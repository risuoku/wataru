from wataru.workflow.provider import (
    Provider,
    provider_generator,
    default_name_function,
)
from wataru.logging import getLogger
import collections
import importlib
import os
import inspect

logger = getLogger(__name__)


# for ChainerProvider

try:
    import chainer
    class ChainerProvider(Provider):
        def build_finished(self):
            for tr_name, tr in self.trainers.items():
                if self._material_location is not None:
                    model_path = os.path.join(self._material_location, tr_name + '.npz')
                    if os.path.isfile(model_path) and self._material_status_completed:
                        chainer.serializers.load_npz(model_path, self.trainers[tr_name])
                        logger.debug('load from saved.')
                    else:
                        if self._material_status_completed:
                            logger.warn('load model failed! .. model not found.')
        
        def run(self):
            tr_names = list(self.trainers.keys())
            for tr_name in tr_names:
                trainer = self.trainers[tr_name]
                logger.debug('trainer {} run start.'.format(tr_name))
                trainer.run()
                if self._material_location is not None:
                    chainer.serializers.save_npz(os.path.join(self._material_location, tr_name + '.npz'), trainer)
                del self.trainers[tr_name] # GPUメモリの解放
                logger.debug('trainer {} run done.'.format(tr_name))
            return self

    # 
    # trainer_factory の仕組みの上でコレを動かすのは難しいか？
    #
    #def simple_chainer_provider_generator(iterator, f, name_function = default_name_function):
    #    if not isinstance(iterator, collections.Iterable):
    #        raise TypeError('`iterator` must be iterable.')
    #    if not f.__name__ == 'transform':
    #        raise ValueError('invalid function name .. {}'.format(f.__name__))
    #    chainer_iterator = [{'transform': ite} for ite in iterator]
    #    return provider_generator(chainer_iterator, [f], name_function = name_function, parent_class = ChainerProvider)

    
    def chainer_provider_generator(iterator, f_list, name_function = default_name_function):
        return provider_generator(iterator, f_list, name_function = name_function, parent_class = ChainerProvider)

except ImportError:
    logger.debug('import ChainerProvider failed!')
