import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base  # your Base = declarative_base()

# Use a separate test DB to avoid clobbering dev data
TEST_DATABASE_URL = "sqlite:///./test.db"  # or use a PostgreSQL test DB

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return engine

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session  # this is the session used in tests

    session.close()
    transaction.rollback()
    connection.close()
