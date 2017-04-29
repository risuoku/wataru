import importlib
from . import create

from .base import CommandBase


# attach models tree
tree = {
    'create': {
        'scenario': create.Scenario(),
        'project': create.Project(),
    }
}
