from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session
from typing_extensions import Annotated

from app.core.dependencies import get_current_user
from app.crud.professors import (
    create_professor,
    delete_professor,
    get_professor,
    list_professors,
    update_professor,
)
from app.db.session import get_session
from app.models.professor import Professor
from app.schemas.errors import Error404Response
from app.schemas.professors import ProfessorCreate, ProfessorRead, ProfessorUpdate

# Define the annotated dependency
SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/", response_model=ProfessorRead)
def create_professor_endpoint(professor: ProfessorCreate, session: SessionDep):
    new_professor = ProfessorCreate(
        full_name=professor.full_name,
        major_id=professor.major_id,
        max_hour=professor.max_hour,
        min_hour=professor.min_hour,
        preferred_days=professor.preferred_days,
        time_slots=professor.time_slots,
    )
    return create_professor(session, new_professor)


@router.get(
    "/{professor_id}",
    response_model=ProfessorRead,
    responses={
        404: {"description": "Professor not found", "model": Error404Response},
    },
)
def get_professor_endpoint(professor_id: int, session: SessionDep):
    professor = get_professor(session, professor_id)
    if not professor:
        return JSONResponse(status_code=404, content={"message": "Professor not found"})
    return professor


@router.get("/", response_model=List[ProfessorRead])
def list_professors_endpoint(session: SessionDep):
    return list_professors(session)


@router.delete(
    "/{professor_id}",
    response_model=dict,
    responses={
        404: {"description": "Professor not found", "model": Error404Response},
    },
)
def delete_professor_endpoint(professor_id: int, session: SessionDep):
    success = delete_professor(session, professor_id)
    if not success:
        return JSONResponse(status_code=404, content={"message": "Professor not found"})
    return {"message": "Professor deleted successfully"}


@router.put("/{professor_id}", response_model=ProfessorRead)
def update_professor_endpoint(
    professor_id: int,
    session: SessionDep,
    professor_data: ProfessorUpdate,
):
    updated_professor = update_professor(session, professor_id, professor_data)
    if not updated_professor:
        raise HTTPException(status_code=404, detail="Professor not found")
    return updated_professor
