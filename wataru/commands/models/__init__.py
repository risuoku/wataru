from . import create
from . import materialize
from . import ls
from . import run


# attach models tree
tree = {
    'create': {
        'scenario': create.Scenario(),
        'project': create.Project(),
    },
    'materialize': materialize.Scenario(),
    'ls': ls.Scenario(),
    'run': run.Materialized(),
}
