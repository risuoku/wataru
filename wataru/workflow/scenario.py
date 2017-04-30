from wataru.logging import getLogger

logger = getLogger(__name__)


class Scenario:
    provider_cls = {}

    def __init__(self, config):
        self._config = config
        self._name = None
        self._loaded_data = None
        self._providers = {}

    def build(self):
        self._name = self._config.get('name', __class__.__name__)
        self._loaded_data = self.load()

        providers = self.__class__.provider_cls
        if isinstance(providers, list):
            providers = dict([(p.__name__, p) for p in providers])

        self._providers = dict([(pc['name'], providers[pc['name']](pc, self._loaded_data)) for pc in self._config['providers']])
        for name, p in self._providers.items():
            p.build()
            logger.debug('provider {} build done.'.format(name))

        return self

    def run(self):
        for name, p in self._providers.items():
            p.run()
            logger.debug('provider {} run done.'.format(name))
        return self

    @property
    def config(self):
        return self._config

    @property
    def providers(self):
        return self._providers

    @property
    def name(self):
        return self._name

    def load(self):
        return None
