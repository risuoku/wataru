from wataru.logging import getLogger
import wataru.workflow.utils as wfutils
import sys
import collections
import inspect

logger = getLogger(__name__)


class Provider:
    trainer_factory = []

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
            if isinstance(rawtf, collections.Iterable):
                # for generator
                for a in rawtf:
                    if inspect.isfunction(a):
                        raise TypeError('invalid type!')
                    tr = a(self.transformed_data)
                    self._trainers[self.get_model_name(getattr(tr, 'name', tr.__class__.__name__))] = tr
            elif inspect.isfunction(rawtf):
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


def default_name_function(d):
    return 'Provider__' + '_'.join(['{}{}'.format(k, v) for k, v in d.items()])


RESERVED_ATTR_NAMES = ['item']
def provider_generator(iterator, f_list, parent_class = Provider, name_function = default_name_function):
    if not isinstance(iterator, collections.Iterable):
        raise TypeError('`iterator` must be iterable.')
    if not isinstance(f_list, collections.Iterable):
        raise TypeError('`f_list` must be iterable.')
    f_names = set([f.__name__ for f in f_list])
    f_dict = dict([(f.__name__, f) for f in f_list])
    for param_dict in iterator:
        if not isinstance(param_dict, dict):
            raise TypeError('`param_dict` must be dict.')
        attrs = {}
        for fname, p in param_dict.items():
            if not isinstance(p, wfutils.param):
                raise TypeError('invalid parameter type!')
            if fname not in f_names:
                raise ValueError('{} not in fnames'.format(fname))
            args, kwargs = p.item
            if fname in RESERVED_ATTR_NAMES:
                raise ValueError('{} is reserved name and not allowed to use.'.format(fname))
            attrs[fname] = (f_dict[fname])(*args, **kwargs)
            attrs['item'] = p.item
            if fname == 'transform':
                d = collections.OrderedDict([(idx, a) for idx, a in enumerate(args)])
                for k, v in sorted(kwargs.items(), key=lambda x: x[0]):
                    d[k] = v
        yield type(
            name_function(d),
            (parent_class,),
            attrs
        )
