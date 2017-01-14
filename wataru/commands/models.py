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
        # get theme
        from wataru.rules import themes
        tm = themes.get_default()

        # setup template loader
        from wataru.rules import templates
        templates.setenv(tm.abs_tpldir)

        # get project rule graph
        from wataru.rules import graph
        rg = graph.get_by_theme(tm)
        project = rg.project

        # add extra nodes
        mddir = rmodels.get_metadatadirectory(project)
        project.add_node(mddir)

        # process project
        project.converge()

        # process meta
        if tm.config.get('meta') is not None:
            mt = tm.config['meta']
            if mt.get('jupyter') is True:
                jobj = rmodels.SetupJupyter(mddir)
                jobj.converge()


class Test(CommandBase):
    options = [
    ]

    def execute(self):
        pass
