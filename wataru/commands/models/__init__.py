from . import project
from . import scenario
from . import material
from . import db
from . import console


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
    'db': {
        'setup': db.Setup(),
    },
    'console': console.Console(),
}
