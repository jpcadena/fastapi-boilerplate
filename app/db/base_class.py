"""
This script defines the base class for SQLAlchemy models
"""

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

Base: type[DeclarativeMeta] = declarative_base()
