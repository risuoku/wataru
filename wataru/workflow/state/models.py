from . import Base

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    SmallInteger,
    ForeignKey,
)
from sqlalchemy.orm import relationship

import datetime
import enum


class Scenario(Base):
    __tablename__ = 'scenarios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    materials = relationship('Material', back_populates='scenario')
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now())


class Material(Base):
    class Status(enum.Enum):
        CREATED = 'created'
        COMPLETED = 'completed'

    __tablename__ = 'materials'

    id = Column(String, primary_key=True, autoincrement=False)
    scenario_id = Column(Integer, ForeignKey('scenarios.id'), nullable=False)
    scenario = relationship('Scenario', back_populates='materials')
    status = Column(String, default=Status.CREATED.value)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now())
