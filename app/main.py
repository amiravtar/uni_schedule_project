from fastapi import FastAPI  # noqa: I001
from app.core.config import settings
from app.db.session import engine
from sqlmodel import SQLModel
from app.routes.major import router as major_router
from app.routes.professors import router as professor_router
from app.routes.auth import router as auth_router
from app.routes.classroom import router as classroom_router
from app.routes.course import router as course_router
from app.routes.solver import router as solver_router
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan_context)  # type: ignore

    # Define the origins that are allowed to make requests to your app
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # Allowed origins
        allow_credentials=True,  # Allow cookies to be sent
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(solver_router, prefix="/solver", tags=["Solver"])
    app.include_router(course_router, prefix="/courses", tags=["Courses"])
    app.include_router(classroom_router, prefix="/classrooms", tags=["Classrooms"])
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
