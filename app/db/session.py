from sqlalchemy import event
from sqlmodel import Session, create_engine

from app.core.config import settings

DATABASE_URL = settings.database_url  # Replace with .env variable later
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


# Enable SQLite foreign key support
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
