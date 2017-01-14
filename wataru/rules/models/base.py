from wataru.logging import getLogger
import wataru.rules.templates as modtpl
import wataru.utils as utils
import os.path
import os
import copy
import re


logger = getLogger(__name__)


class RuleBase:
    def converge(self):
        raise NotImplementedError()

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
            utils.save_file(self.abspath, content)
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

        self._converge_children()

    def add_node(self, node):
        if not (isinstance(node, DirectoryBase) or isinstance(node, FileBase)):
            raise TypeError('node must be DirectoryBase or FileBase object')
        if isinstance(node, DirectoryBase):
            self._children_dir.append(node)
        else:
            self._children_file.append(node)

    def _converge_children(self):
        children = self._children_dir + self._children_file
        for c in children:
            c.converge()
