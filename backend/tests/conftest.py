import os
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure JWT signing key is available before importing auth
os.environ.setdefault("JWT_SECRET", "testsecret")
# Ensure legacy tests that import app.database.SessionLocal never fall back to
# the developer PostgreSQL URL during collection.
LEGACY_TEST_DB_PATH = Path(".pytest_legacy.db")
LEGACY_TEST_DB_PATH.unlink(missing_ok=True)
os.environ.setdefault("DATABASE_URL", f"sqlite:///./{LEGACY_TEST_DB_PATH}")
WORKSPACE_TMP_PATH = Path(".pytest_tmp")
WORKSPACE_TMP_PATH.mkdir(exist_ok=True)
os.environ.setdefault("TMP", str(WORKSPACE_TMP_PATH.resolve()))
os.environ.setdefault("TEMP", str(WORKSPACE_TMP_PATH.resolve()))

from app.models import Base  # your Base = declarative_base()
from app.database import engine as legacy_engine

Base.metadata.create_all(bind=legacy_engine)


def pytest_configure(config):
    config.option.basetemp = str((WORKSPACE_TMP_PATH / "basetemp").resolve())

# Use an in-memory test DB to avoid creating real tables on disk
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
from sqlalchemy import event

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture(scope="function")
def db_session(db_engine):
    Base.metadata.drop_all(bind=db_engine)
    Base.metadata.create_all(bind=db_engine)
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session  # this is the session used in tests

    session.close()
    transaction.rollback()
    connection.close()
