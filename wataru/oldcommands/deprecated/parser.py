import argparse
import wataru.commands.deprecated.models as cmdmodels
import wataru.utils as utils
import importlib

_description = 'process wataru commands'
_cls_subcommands = [getattr(cmdmodels, a) for a in cmdmodels.__all__]


class WataruArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(WataruArgumentParser, self).__init__(description=_description)
    
    def build(self):
        # build for subcommands
        subparsers = self.add_subparsers(help='wataru commands help')
        for cls in _cls_subcommands:
            p_name = utils.camel2snake(cls.__name__)
            subp = subparsers.add_parser(p_name, help='{} help'.format(p_name))
            options = cls.default_options + cls.options
            for op in options:
                args, kwargs = op.item
                subp.add_argument(*args, **kwargs)
        return self

    def parse_and_create(self, args, subcmd):
        raw_ns = self.parse_args(args = args)
        if subcmd is not None:
            cls = getattr(cmdmodels, utils.snake2camel(subcmd))
            return cls(raw_ns)
        else:
            return None


def get():
    parser = WataruArgumentParser(_description)
    return parser.build()
