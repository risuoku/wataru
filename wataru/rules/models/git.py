from .base import RuleBase

__all__ = [
    'Gitignore',
]


class Gitignore(RuleBase):
    filename = '.gitignore'
    dirpath = ''
    required = True
