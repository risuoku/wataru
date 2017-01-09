from .base import (
    FileBase,
    DirectoryBase,
)

__all__ = ['EmptyFile', 'EmptyDirectory',]


class EmptyFile(FileBase):
    pass


class EmptyDirectory(DirectoryBase):
    pass
