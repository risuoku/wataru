from wataru.logging import getLogger

import wataru.rules.models as rmodels

__all__ = ['CreateProject', 'Test',]

logger = getLogger(__name__)


class Option:
    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs
    
    @property
    def item(self):
        return self._args, self._kwargs


class CommandBase:
    default_options = [
        Option('-v', '--verbose', dest='verbose', action='store_true', default=False),
    ]
    options = []

    def __init__(self, ns):
        self._ns = ns

    def execute(self):
        raise NotImplementedError()


class CreateProject(CommandBase):
    options = [
        Option('--name', action='store', dest='projectname'),
        Option('--root-dir', action='store', dest='rootdir', default=''),
    ]

    def execute(self):
        # get project rule graph
        from wataru.rules import graph
        rg = graph.get_default()

        # process project
        rg.project.converge()

        # process virtualenv
        logger.debug('process Virtualenv')
        obj_virtualenv = rmodels.Virtualenv(rootdir=self._ns.rootdir)
        obj_virtualenv.converge()


class Test(CommandBase):
    options = [
    ]

    def execute(self):
        pass
