from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlmodel import Session
from typing_extensions import Annotated

from app.core.dependencies import get_current_user
from app.crud.course import list_courses
from app.crud.professors import list_professors
from app.crud.solver import (
    create_solver_resualt,
    delete_solver_resualt,
    get_solver_resualt,
    list_solver_resualts,
)
from app.db.session import get_session
from app.schemas.course import CourseRead
from app.schemas.errors import Error404Response
from app.schemas.professors import ProfessorRead
from app.schemas.solver import (
    CourceTimeSlots,
    SolverHistoryResualtCreate,
    SolverHistoryResualtRead,
    SolverHistoryResualtReadLight,
    SolverResualt,
    SolverSettings,
    SolverSolution,
)
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
    settings.debug=True
    model = ModelSolver(data=model_data, settings=settings, professors=dict_professors)
    try:
        data: list[list[tuple[int, CourceTimeSlots, int]]] = model.solve()
        if len(data) == 0 or len(data[0]) == 0:
            raise ValueError("جوابی پیدا نشد")
        output_sols: list[SolverSolution] = parse_solver_output(
            sols=data, input_courses=model_data, professors=dict_professors
        )
        solver_history_resualt = create_solver_resualt(
            session=session,
            solver_resualt_data=SolverHistoryResualtCreate(
                name=settings.solver_resualt_name, resualt=output_sols
            ),
        )

        solver_resualt = SolverResualt(
            Solutions=output_sols,
            settings=settings,
            solver_resualt_history=SolverHistoryResualtReadLight(
                **solver_history_resualt.model_dump()
            ),
        )
        return solver_resualt
    except ValueError as ex:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(ex)},
        )
    except Exception as ex:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(ex)
        )


@router.post("/resualt/", response_model=SolverHistoryResualtReadLight)
def create_solver_resualt_endpoint(
    solver_resualt: SolverHistoryResualtCreate, session: SessionDep
):
    new_solver_resualt = create_solver_resualt(session, solver_resualt)
    return new_solver_resualt


@router.get(
    "/resualt/{solver_resualt_id}",
    response_model=SolverHistoryResualtRead,
    responses={
        404: {"description": "Solver result not found", "model": Error404Response},
    },
)
def get_solver_resualt_endpoint(solver_resualt_id: int, session: SessionDep):
    solver_resualt = get_solver_resualt(session, solver_resualt_id)
    if not solver_resualt:
        return JSONResponse(
            status_code=404, content={"message": "Solver result not found"}
        )
    return solver_resualt


@router.get("/resualt/", response_model=list[SolverHistoryResualtReadLight])
def list_solver_resualts_endpoint(session: SessionDep):
    return list_solver_resualts(session)


@router.delete(
    "/resualt/{solver_resualt_id}",
    response_model=dict,
    responses={
        404: {"description": "Solver result not found", "model": Error404Response},
    },
)
def delete_solver_resualt_endpoint(solver_resualt_id: int, session: SessionDep):
    success = delete_solver_resualt(session, solver_resualt_id)
    if not success:
        return JSONResponse(
            status_code=404, content={"message": "Solver result not found"}
        )
    return {"message": "Solver result deleted successfully"}
