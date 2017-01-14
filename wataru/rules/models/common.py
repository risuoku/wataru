from .base import (
    FileBase,
    DirectoryBase,
)
import os
import wataru.utils as utils
from wataru.logging import getLogger

__all__ = [
    'ProjectRoot',
    'get_metadatadirectory',
]

logger = getLogger(__name__)


class ProjectRoot(DirectoryBase):
    def __init__(self, rootdir, name = 'sample', virtualenv = True):
        super(ProjectRoot, self).__init__(name = name)
        self._abs_rootdir = os.path.abspath(rootdir)
        self._virtualenv = virtualenv

    def converge(self):
        abspath = self.abspath
        logger.debug('target: {}'.format(abspath))

        if os.path.isdir(abspath):
            logger.debug('already exist')
        else:
            if not self._virtualenv:
                os.makedirs(abspath)
            else:
                cmd = 'virtualenv {}'.format(abspath)
                utils.do_console_command(cmd)
            logger.debug('created normally')

        self._converge_children()

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


class MetadataDirectory(DirectoryBase):
    name_default = '.wataru'

    @property
    def metadata(self):
        for fo in self._children_file:
            if isinstance(fo, Metadata):
                return fo
        raise AttributeError('metadata not found!')

class Metadata(FileBase):
    name_default = 'metadata.yml'


def get_metadatadirectory(p):
    mddir = MetadataDirectory(parent = p)
    md = Metadata(parent = mddir)
    mddir.add_node(md)
    return mddir
