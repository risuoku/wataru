from wataru.commands.models.base import CommandBase
from wataru.logging import getLogger

import wataru.workflow.state as wfstate


logger = getLogger(__name__)


class Setup(CommandBase):
    def apply_arguments(self, parser):
        parser.add_argument('--config-path', action='store', dest='configpath', default='')

    def execute(self, namespace):
        wfstate.create_all()
