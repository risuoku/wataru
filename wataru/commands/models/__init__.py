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
        'sync': scenario.Sync(),
        'rm': scenario.Rm(),
    },
    'material': {
        'ls': material.Ls(),
        'run': material.Run(),
        'rm': material.Rm(),
    },
    'db': {
        'setup': db.Setup(),
    },
    'console': console.Console(),
}
