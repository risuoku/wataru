from .base import (
    FileBase,
    DirectoryBase,
)

__all__ = [
    'DocsDirectory',
    'ProjectSummary',
]

class DocsDirectory(DirectoryBase):
    name = 'docs'
    required = True


class ProjectSummary(FileBase):
    name = 'summary.md'
    required = True
