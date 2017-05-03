from wataru.logging import getLogger
import wataru.workflow.utils as wfutils
import sys
import collections

logger = getLogger(__name__)


class Provider:
    def __init__(self, config, data, package_name, material_location):
        self._config = config
        self._data = data
        self._package_name = package_name
        self._material_location = material_location
        self._trainers = {}

    def build(self, with_saved = False):
        return self

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


def default_name_function(d):
    return 'Provider__' + '_'.join(['{}{}'.format(k, v) for k, v in d.items()])


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
        methods = {}
        for fname, p in param_dict.items():
            if not isinstance(p, wfutils.param):
                raise TypeError('invalid parameter type!')
            if fname not in f_names:
                raise ValueError('{} not in fnames'.format(fname))
            args, kwargs = p.item
            d = collections.OrderedDict([(idx, a) for idx, a in enumerate(args)])
            for k, v in sorted(kwargs.items(), key=lambda x: x[0]):
                d[k] = v
            methods[fname] = (f_dict[fname])(*args, **kwargs)
        yield type(
            name_function(d),
            (parent_class,),
            methods
        )
