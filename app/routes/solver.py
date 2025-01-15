from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session
from typing_extensions import Annotated

from app.core.dependencies import get_current_user
from app.crud.course import list_courses
from app.db.session import get_session
from app.schemas.course import CourseRead
from app.schemas.solver import Courses as SolverCourse
from app.schemas.solver import SolverSettings
from app.solver.solver import ModelSolver
from app.utils.parser import convert_course_read_list_to_solver_course_list

SessionDep = Annotated[Session, Depends(dependency=get_session)]

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post(
    "/solve",
)
def solve(settings: SolverSettings, session: SessionDep):
    courses: list[CourseRead] = [
        CourseRead.model_validate(course, from_attributes=True)
        for course in list_courses(session)
    ]
    model_data: list[SolverCourse] = convert_course_read_list_to_solver_course_list(
        courses
    )
    model = ModelSolver(data=model_data, settings=settings)
    data=model.solve()
    return {"data": data}
