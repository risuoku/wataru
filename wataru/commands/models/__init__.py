from . import project
from . import scenario
from . import material


# attach models tree

tree = {
    'project': {
        'create': project.Create(),
    },
    'scenario': {
        'materialize': scenario.Materialize(),
        'ls': scenario.Ls(),
    },
    'material': {
        'ls': material.Ls(),
        'run': material.Run(),
    },
}
