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
        Option('--root-dir', action='store', dest='rootdir'),
        Option('--enable-virtualenv', action='store_true', default=False, dest='virtualenv_enabled'),
        Option('--theme-dir', action='store', dest='themedir'),
    ]

    def execute(self):
        # get theme
        from wataru.rules import themes
        tm = themes.get_default() if self._ns.themedir is None else themes.get(self._ns.themedir)

        # update theme
        if self._ns.projectname is not None:
            tm.update_project('name', self._ns.projectname)
        if self._ns.rootdir is not None:
            tm.update_project('rootdir', self._ns.rootdir)
        if self._ns.virtualenv_enabled:
            tm.update_project('virtualenv', True)

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
        mt = tm.config['meta']
        jobj = rmodels.SetupJupyter(mddir, project.abspath, mt.get('jupyter'))
        jobj.converge()


class Test(CommandBase):
    options = [
    ]

    def execute(self):
        pass
