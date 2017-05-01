from . import Base

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)

import datetime


class Scenario(Base):
    __tablename__ = 'scenarios'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now())
    updated_at = Column(DateTime, default=datetime.datetime.now())
