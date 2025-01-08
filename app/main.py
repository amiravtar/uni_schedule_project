from fastapi import FastAPI  # noqa: I001
from app.core.config import settings
from app.db.session import engine
from app.models import Major
from sqlmodel import SQLModel
from app.routes.major import router as major_router
from app.routes.professors import router as professor_router
from app.routes.auth import router as auth_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan_context)  # type: ignore
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(professor_router, prefix="/professors", tags=["Professors"])
    app.include_router(major_router, prefix="/majors", tags=["Majors"])
    return app


async def lifespan_context(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = create_app()


@app.get("/")
async def home():
    return {"message": "Hello World"}
