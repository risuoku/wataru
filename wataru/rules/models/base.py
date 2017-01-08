from wataru.logging import getLogger
import wataru.rules.templates as modtpl
import os.path
import os

__all__ = [
    'ProjectRoot',
    'Virtualenv',
]

logger = getLogger(__name__)


class RuleBase:
    def __init__(self, rootdir = '', render_param = {}, projectname = 'sample_ml_project'):
        self._rootdir = rootdir
        self._render_param = render_param
        self._projectname = projectname

    def converge(self):
        tplpath = os.path.join(self.dirpath, self.filename + '.tpl')
        tpl = modtpl.get(tplpath)
        print(tpl.render(**self._render_param))

    def validate(self):
        raise NotImplementedError()


class ProjectRoot(RuleBase):

    def converge(self):
        targetdir = os.path.join(self._rootdir, self._projectname)
        if not os.path.isabs(targetdir):
            targetdir = os.path.join(os.getcwd(), targetdir)
        logger.debug('project_targetdir: {}'.format(targetdir))

        if os.path.isdir(targetdir):
            logger.debug('already exist')
        else:
            os.makedirs(targetdir)
            logger.debug('created normally')

    def validate(self):
        pass


class Virtualenv(RuleBase):

    def converge(self):
        pass

    def validate(self):
        pass
