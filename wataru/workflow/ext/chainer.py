from wataru.workflow.model import (
    Model,
    model_generator,
)
from wataru.logging import getLogger
from wataru.utils import get_hash
import collections
import importlib
import os
import inspect

import chainer

logger = getLogger(__name__)


class ChainerModel(Model):
    def prepare_finished(self, mode):
        model_path, is_valid_path = self.get_model_filepath_name()
        if is_valid_path:
            chainer.serializers.load_npz(model_path, self.value)
            logger.debug('{} .. load from saved.'.format(self.name))
        else:
            if mode == 'load':
                raise Exception('{} .. load model failed! .. model not found.'.format(self.name))

    def fit(self):
        if not isinstance(self.value, chainer.training.Trainer):
            raise TypeError('{} must be chainer.training.Trainer'.format(self.value))
        self.value.run()

    def save(self):
        model_path, is_valid_path = self.get_model_filepath_name()
        if not is_valid_path:
            chainer.serializers.save_npz(model_path, self.value)
        logger.debug('save {} done.'.format(self.name))

    def get_model_filepath_name(self):
        model_path = os.path.join(self.material_location, get_hash(self.name) + '.npz')
        return model_path, os.path.isfile(model_path)
