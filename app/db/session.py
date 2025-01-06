from sqlmodel import Session, create_engine

from app.core.config import settings

DATABASE_URL = settings.database_url  # Replace with .env variable later
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session
