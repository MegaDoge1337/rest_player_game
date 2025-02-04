import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_connection_string = os.environ.get("DB_CONNECTION_STRING")
_pool_size = int(os.environ.get("DB_POOL_SIZE", "5"))
_max_overflow = int(os.environ.get("DB_MAX_OVERFLOW", "10"))

engine = create_engine(_connection_string, pool_size=_pool_size, max_overflow=_max_overflow)
SessionFactory = sessionmaker(bind=engine)
