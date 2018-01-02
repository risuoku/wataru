from wataru.logging import getLogger

import wataru.workflow.utils as wfutils
import collections
import os
from wataru.utils import (
    cache_located_at,
    get_hash,
)

logger = getLogger(__name__)


class ModelManager:
    model_generator = []

    def __init__(self, rawdata, material_location, is_materialized):
        self.model_classes = {}
        self.models = {}
        self.data = None
        self.rawdata = rawdata
        self.material_location = material_location
        self.is_materialized = is_materialized

    def build_models(self):
        model_names_dc = wfutils.DuplicateChecker()

        # build model classes
        for mc in self.__class__.model_generator:
            model_names_dc.add(mc.__name__)
            self.model_classes[self.name() + '**' + mc.__name__] = mc

        transform = self.transform
        if self.is_materialized: # use cache if materialized
            transform = cache_located_at(
                os.path.join(self.material_location, 'transformed_' + get_hash(self.name()) + '.pickle'),
                cache_must_exist = (self.rawdata is None)
            )(transform)
        self.data = transform() 
        for name, mc in self.model_classes.items():
            self.models[name] = mc(self.data, self.material_location, name)
            logger.debug('model {} build done.'.format(name))

    def train_all(self):
        for name, mo in self.models.items():
            if self.is_materialized:
                self.train(name)
            else:
                self.train_without_materialized(name)
        return self

    def prepare_all(self):
        for name, mo in self.models.items():
            self.prepare(name)
        return self

    def train(self, name):
        target = self.models[name]
        target.prepare()
        target.prepare_finished('train')
        target.fit()
        target.save()
        return self

    def train_without_materialized(self, name):
        target = self.models[name]
        target.prepare()
        target.fit()
        return self

    def prepare(self, name):
        target = self.models[name]
        target.prepare()
        target.prepare_finished('load')
        return self

    def transform(self):
        return self.data

    def name(self):
        return self.__class__.__name__


def _wrap_transform(transform_function):
    def _func(mm):
        data = mm.rawdata
        args, kwargs = mm.param.item
        return transform_function(data, args, kwargs)
    return _func


def manager_generator(transform_function = None, configs = [], parent_class = ModelManager):
    if not isinstance(configs, collections.Iterable):
        raise TypeError('`configs` must be Iterable.')
    for config in configs:
        _param = wfutils.param() if 'param' not in config else wfutils.get_converted_param(config['param'])
        _model_generator = [] if 'model_generator' not in config else config['model_generator']
        if not isinstance(_model_generator, collections.Iterable):
            raise TypeError('`model_generator` must be Iterable.')
        class_name = parent_class.__name__ + '|' + _param.name
        attrs = {
            'param': _param,
            'model_generator': _model_generator
        }
        if transform_function is not None:
            attrs['transform'] = _wrap_transform(transform_function)
        yield type(
            class_name,
            (parent_class,),
            attrs,
        )
