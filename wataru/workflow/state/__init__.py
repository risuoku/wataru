from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from contextlib import contextmanager
import sys


# prepare Base class
Base = declarative_base()


# state module attributes
engine = None
SessionCls = None
setup_done = False
cached_session = None


# helper methods
def setup(d):
    if not isinstance(d, dict):
        raise TypeError('setting must be dict.')
    self = sys.modules[__name__]

    try:
        # build engine
        if d.get('uri') is None:
            self.engine = create_engine('sqlite:///:memory:', echo=True)
        else:
            self.engine = create_engine(d['uri'], echo=True)

        # build SessionCls
        self.SessionCls = sessionmaker(bind=self.engine)

        # notify setup done
        self.setup_done = True

    except Exception:
        self.setup_done = False
        raise


def _check_setup_done():
    if not setup_done:
        raise Exception('{} is not ready.'.format(__name__))


def create_all():
    _check_setup_done()
    Base.metadata.create_all(engine)


def get_session():
    _check_setup_done()
    if cached_session is None:
        sys.modules[__name__].cached_session = SessionCls()
    return cached_session


@contextmanager
def session_scope():
    _check_setup_done()
    session = SessionCls()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


# import models
from .models import Scenario
