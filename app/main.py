from fastapi import FastAPI  # noqa: I001
from app.core.config import settings
from app.db.session import engine
from app.models import Major
from sqlmodel import SQLModel


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan_context)
    return app


async def lifespan_context(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = create_app()


@app.get("/")
async def home():
    return {"message": "Hello World"}
