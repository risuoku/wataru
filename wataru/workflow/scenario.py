from wataru.logging import getLogger

from wataru.workflow.state import (
    Material as ModelMaterial,
    session_scope,
    get_session,
)

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
        self._package_name = None
        self._material_location = None
        self._provider_build_with_saved = False

    def build(self):
        self._name = self._config.get('name', __class__.__name__)
        self._loaded_data = self.load()

        providers = self.__class__.provider_cls
        if isinstance(providers, list):
            providers = dict([(p.__name__, p) for p in providers])

        self._providers = dict([(pc['name'], providers[pc['name']](pc, self._loaded_data, self._package_name, self._material_location)) for pc in self._config['providers']])
        for name, p in self._providers.items():
            p.build(with_saved = self._provider_build_with_saved)
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

    def set(self, key, value):
        setattr(self, '_' + key, value)


def build(material_id, settings, need_not_completed = False):
    target_dir = os.path.join(settings['materialized_dir'], material_id)
    if os.path.isdir(target_dir):
        sys.path.append(settings['materialized_dir'])
        smod = importlib.import_module(material_id + '.' + settings['scenario_entry_module_name'])
        sobj = getattr(smod, settings['scenario_entry_function_name'])()

        # inject runtime attributes
        sobj.set('package_name', material_id)
        sobj.set('material_location', target_dir)

        # check status
        rosess = get_session()
        mm = rosess.query(ModelMaterial).filter_by(status=ModelMaterial.Status.COMPLETED.value, id=material_id)
        if mm.count() > 0:
            # raise Exception
            if need_not_completed:
                raise Exception('{} already completed.'.format(material_id))

            # already completed
            sobj.set('provider_build_with_saved', True)
        return sobj.build()
    else:
        raise Exception('material not found!')


def run(material_id, settings):
    sobj = build(material_id, settings, need_not_completed = True)
    with session_scope() as session:
        # update meta
        mm = session.query(ModelMaterial).filter_by(id=material_id).first()
        mm.updated_at = datetime.datetime.now()
        mm.status = ModelMaterial.Status.COMPLETED.value

        # run
        sobj.run()
    logger.debug('run {} done.'.format(material_id))
