class CommandBase:
    def apply_arguments(self, parser):
        pass

    def execute(self, namespace):
        raise NotImplementedError()
