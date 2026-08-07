from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from app.operational_config import load_operational_settings

operational_settings = load_operational_settings()
DATABASE_URL = operational_settings.database_url

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

if DATABASE_URL.startswith("sqlite"):
    from sqlalchemy import event

    def _fk_pragma_on_connect(dbapi_con, con_record):
        cursor = dbapi_con.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    event.listen(engine, "connect", _fk_pragma_on_connect)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.models import Base
from app.observability import emit_event, metrics

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError:
        db.rollback()
        metrics.increment("echoed_database_operations_total", operation="session", result="failure")
        emit_event("database.operation_failed", level=40, component="database", operation="session", result="failure")
        raise
    finally:
        db.close()
