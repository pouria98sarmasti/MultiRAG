"""
Base database model for SQLAlchemy with async support.

This module provides the base model for all database models
with SQLAlchemy ORM functionality.
"""

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

import pytz
from datetime import datetime

# ensure local time is used
# must remove time zone info to be able use in postgresql
# if use DateTime(timezone=True) postgresql will always use UTC time
# even changing PostgreSQL's timezone setting it only affect displayed time to user not stored value for time (which is always UTC when use timezone aware time)
CURRENT_TIME = lambda: datetime.now(pytz.timezone('Asia/Tehran')).replace(tzinfo=None)



class Base(AsyncAttrs, DeclarativeBase, MappedAsDataclass):
    """Base class for all SQLAlchemy database models."""
    pass 