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
        # process project root dir
        logger.debug('process ProjectRoot')
        obj_project_root = rmodels.ProjectRoot(rootdir=self._ns.rootdir)
        obj_project_root.converge()

        # process virtualenv
        logger.debug('process Virtualenv')
        obj_virtualenv = rmodels.Virtualenv(rootdir=self._ns.rootdir)
        obj_virtualenv.converge()

        # process rules
        cls_all_rules = [getattr(rmodels, a) for a in rmodels.RULE_LIST]
        for cls in cls_all_rules:
            logger.debug('process {}'.format(cls.__name__))
            obj = cls(rootdir=self._ns.rootdir)
            obj.converge()


class Test(CommandBase):
    options = [
    ]

    def execute(self):
        pass
