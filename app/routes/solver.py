from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlmodel import Session
from typing_extensions import Annotated

from app.core.dependencies import get_current_user
from app.crud.course import list_courses
from app.crud.professors import list_professors
from app.db.session import get_session
from app.schemas.course import CourseRead
from app.schemas.professors import ProfessorRead
from app.schemas.solver import CourceTimeSlots, SolverResualt, SolverSettings
from app.schemas.solver import Courses as SolverCourse
from app.solver.solver import ModelSolver
from app.utils.parser import (
    convert_course_read_list_to_solver_course_list,
    parse_solver_output,
)

SessionDep = Annotated[Session, Depends(dependency=get_session)]

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post(
    "/solve",
    responses={
        400: {
            "description": "Something is wrong with the input data",
        },
    },
    response_model=SolverResualt,
)
def solve(settings: SolverSettings, session: SessionDep):
    courses: list[CourseRead] = [
        CourseRead.model_validate(course, from_attributes=True)
        for course in list_courses(session)
    ]
    professors: list[ProfessorRead] = [
        ProfessorRead.model_validate(professor, from_attributes=True)
        for professor in list_professors(session=session)
    ]
    model_data: list[SolverCourse] = convert_course_read_list_to_solver_course_list(
        courses
    )
    dict_professors = {p.id: p for p in professors}
    model = ModelSolver(data=model_data, settings=settings, professors=dict_professors)
    try:
        data: list[list[tuple[int, CourceTimeSlots, int]]] = model.solve()
        output_data = parse_solver_output(sols=data, input_courses=model_data,professors=dict_professors)
        return output_data
    except ValueError as ex:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(ex)},
        )
    except Exception as ex:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(ex)
        )
