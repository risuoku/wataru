import sys
import os
import importlib

_modulename2alias = [
    ('numpy', 'np'),
    ('pandas', 'pd'),
]


if __name__ == '__main__':
    # import modules
    for name, alias in _modulename2alias:
        mod = importlib.import_module(name)
        setattr(sys.modules[__name__], alias or name, mod)

    # setup custom pythonpath
    modules_dir_name = os.path.join(os.path.dirname(os.getcwd()), 'modules')
    if os.path.isdir(modules_dir_name):
        sys.path.append(modules_dir_name)
