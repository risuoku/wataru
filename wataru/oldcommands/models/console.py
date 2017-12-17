from wataru.commands.models.base import CommandBase
from wataru.logging import getLogger
import code

logger = getLogger(__name__)


class Console(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')

    def execute(self, namespace):
        code.interact(local=globals())
