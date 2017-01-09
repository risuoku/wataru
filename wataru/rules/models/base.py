from wataru.logging import getLogger
import wataru.rules.templates as modtpl
import os.path
import os
import copy
import re

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


class NodeBase(RuleBase):
    name_default = ''
    required_default = False

    def __init__(self, parent = None, name = None):
        self._config = None
        self._absparentpath = None
        self._parentpath = None
        if parent is not None:
            self._config = copy.copy(parent.config)
            self._absparentpath = os.path.join(parent.absparentpath, parent.name)
            self._parentpath = os.path.join(parent.parentpath, parent.name)
        self._name = name

    def validate(self):
        pass
    
    @property
    def config(self):
        return self._config

    @property
    def name(self):
        name = self._name or self.__class__.name_default
        if name is None or name == '':
            raise ValueError('directory name must be set')
        return name

    @property
    def absparentpath(self):
        return self._absparentpath

    @property
    def parentpath(self):
        return re.sub(self.config['projectname'], '', self._parentpath)

    @property
    def abspath(self):
        return os.path.join(self.absparentpath, self.name)

    @property
    def path(self):
        return os.path.join(self.parentpath, self.name)


class FileBase(NodeBase):

    def converge(self):
        abspath = self.abspath
        logger.debug('target: {}'.format(abspath))

        if os.path.isfile(abspath):
            logger.debug('already exist')
        else:
            tplpath = os.path.join(self.parentpath, self.name + '.tpl')
            tpl = modtpl.get(tplpath)
            content = tpl.render(**self.config)
            with open(self.abspath, 'w', encoding='utf-8') as f:
                f.write(content + '\n')
            logger.debug('created normally')

    def validate(self):
        pass


class DirectoryBase(NodeBase):

    def __init__(self, parent = None, name = None):
        super(DirectoryBase, self).__init__(parent = parent, name = name)
        self._children_dir = []
        self._children_file = []

    def converge(self):
        abspath = self.abspath
        logger.debug('target: {}'.format(abspath))

        if os.path.isdir(abspath):
            logger.debug('already exist')
        else:
            os.makedirs(abspath)
            logger.debug('created normally')

        # recursive converge
        children = self._children_dir + self._children_file
        for c in children:
            c.converge()

    def add_node(self, node):
        if not (isinstance(node, DirectoryBase) or isinstance(node, FileBase)):
            raise TypeError('node must be DirectoryBase or FileBase object')
        if isinstance(node, DirectoryBase):
            self._children_dir.append(node)
        else:
            self._children_file.append(node)


class ProjectRoot(DirectoryBase):
    def __init__(self, rootdir, name = 'ml_sample_project'):
        super(ProjectRoot, self).__init__(name = name)
        self._abs_rootdir = os.path.abspath(rootdir)

    @property
    def absparentpath(self):
        return self._abs_rootdir

    @property
    def parentpath(self):
        return ''

    @property
    def config(self):
        return {
            'projectname': self.name,
        }


class Virtualenv(RuleBase):

    def converge(self):
        pass

    def validate(self):
        pass
