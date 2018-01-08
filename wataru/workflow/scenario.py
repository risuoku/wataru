from wataru.logging import getLogger

from wataru.workflow.state import (
    Material as ModelMaterial,
    session_scope,
    get_session,
)
from wataru.workflow.manager import ModelManager

import wataru.workflow.state as wfstate
import wataru.workflow.utils as wfutils

import os
import sys
import importlib
import pickle
import datetime
import collections

logger = getLogger(__name__)


class Scenario:
    manager_cls = []

    def __init__(self, package_name, material_location, material_status):
        self.name = None
        self.loaded_data = None
        self.managers = {}
        self.package_name = package_name
        self.material_location = material_location
        self.material_status = material_status

    def build_managers(self, load_enabled, is_materialized):
        self.name = self.__class__.__name__

        if load_enabled:
            self.loaded_data = self.load()

        raw_managers = self.__class__.manager_cls
        managers = collections.OrderedDict()
        if not isinstance(raw_managers, collections.Iterable):
            raw_managers = [raw_managers]

        manager_names_dc = wfutils.DuplicateChecker()
        for rawm in raw_managers:
            if isinstance(rawm, collections.Iterable):
                # for generator
                for a in rawm:
                    if not issubclass(a, ModelManager):
                        raise TypeError('invalid type!')
                    manager_names_dc.add(a.__name__)
                    managers[a.__name__] = a
            elif issubclass(rawm, ModelManager):
                # just manager
                manager_names_dc.add(rawm.__name__)
                managers[rawm.__name__] = rawm
            else:
                raise TypeError('invalid type!')
        
        logger.debug('registered managers .. {}'.format(', '.join([k for k, v in managers.items()])))
        self.managers = dict([
            (mname, m(self.loaded_data, self.material_location, is_materialized))
            for mname, m in managers.items()
        ])
        for name, m in self.managers.items():
            m.build_models()
            logger.debug('manager {} build done.'.format(name))

        return self

    def train_all(self):
        for name, m in self.managers.items():
            m.train_all()
            logger.debug('manager {} train_all done.'.format(name))
        return self

    def prepare_all(self):
        for name, m in self.managers.items():
            m.prepare_all()
            logger.debug('manager {} prepare_all done.'.format(name))
        return self

    def get_model_by_hash(self, hashed_id):
        target = None
        for mgr in self.managers.values():
            for mdl in mgr.models.values():
                if mdl.get_hashed_id() == hashed_id:
                    target = mdl
                    break
        if target is None:
            raise ValueError('hashed_id: {} not found.'.format(hashed_id))
        return target

    def load(self):
        return None
