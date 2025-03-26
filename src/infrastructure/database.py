import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_connection_string = os.environ.get("DB_CONNECTION_STRING")

if not _connection_string:
    raise ValueError("Environment variable `DB_CONNECTION_STRING` not defined.")

_pool_size = int(os.environ.get("DB_POOL_SIZE"))

if not _pool_size:
    raise ValueError("Environment variable `DB_POOL_SIZE` not defined.")

_max_overflow = int(os.environ.get("DB_MAX_OVERFLOW"))

if not _max_overflow:
    raise ValueError("Environment variable `DB_MAX_OVERFLOW` not defined.")


engine = create_engine(
    _connection_string, pool_size=_pool_size, max_overflow=_max_overflow
)
SessionFactory = sessionmaker(bind=engine)
