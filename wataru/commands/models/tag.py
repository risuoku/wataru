from wataru.commands.models.base import CommandBase
from wataru.logging import getLogger
import code
from wataru.workflow.state import (
    session_scope,
    Material,
)

logger = getLogger(__name__)


class Tag(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')
        parser.add_argument('input', nargs='+')

    def execute(self, namespace):
        _input = namespace.input
        if not len(_input) == 2:
            raise ValueError('invalid input .. tag input must be [material_id] [tag]')
        mid = _input[0]
        tag = _input[1]
        with session_scope() as session:
            target = session.query(Material).filter_by(id=mid).first()
            if target is None:
                raise ValueError('target not found.')
            target.tag = tag
