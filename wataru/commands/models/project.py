from wataru.commands.models.base import CommandBase
from wataru.logging import getLogger
import wataru.rules.models as rmodels

import os
import sys

logger = getLogger(__name__)


class Create(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--name', action='store', dest='projectname'),
        parser.add_argument('--root-dir', action='store', dest='rootdir'),
        parser.add_argument('--enable-virtualenv', action='store_true', default=False, dest='virtualenv_enabled'),
        parser.add_argument('--theme-dir', action='store', dest='themedir'),

    def execute(self, namespace):
        # get theme
        from wataru.rules import themes
        tm = themes.get_default() if namespace.themedir is None else themes.get(namespace.themedir)

        # update theme
        if namespace.projectname is not None:
            tm.update_project('name', namespace.projectname)
        if namespace.rootdir is not None:
            tm.update_project('rootdir', namespace.rootdir)
        if namespace.virtualenv_enabled:
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
