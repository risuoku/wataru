from wataru.logging import getLogger

import os
import sys
import importlib
import pickle
import datetime

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


def run(materialized_id, settings):
    target_dir = os.path.join(settings['materialized_dir'], materialized_id)
    if os.path.isdir(target_dir):
        sys.path.append(settings['materialized_dir'])
        smod = importlib.import_module(materialized_id + '.' + settings['scenario_entry_module_name'])
        sobj = getattr(smod, settings['scenario_entry_function_name'])()

        # check status
        meta_file = os.path.join(settings['materialized_dir'], 'meta.pickle')
        with open(meta_file, 'rb') as f:
            db_meta = pickle.load(f)
        _found = False
        _idx = None
        for idx, c in enumerate(db_meta['name2id'][sobj.name]):
            if c['id'] == materialized_id:
                _idx = idx
                _found = True
                break
        if not _found:
            raise Exception('unknown error occured!')
        
        if db_meta['name2id'][sobj.name][_idx]['status'] == 'completed':
            raise Exception('{} already completed.'.format(materialized_id))

        # run
        sobj.run()

        # update meta
        _now = datetime.datetime.now()
        db_meta['name2id'][sobj.name][_idx].update({
            'updated_at': _now,
            'status': 'completed',
        })
        with open(meta_file, 'wb') as f:
            pickle.dump(db_meta, f)
        logger.debug('run {} done.'.format(materialized_id))
    else:
        raise Exception('materialized not found!')
