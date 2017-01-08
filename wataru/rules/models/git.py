from .base import FileBase

__all__ = [
    'Gitignore',
]


class Gitignore(FileBase):
    name = '.gitignore'
    required = True
