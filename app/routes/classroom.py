from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session
from typing_extensions import Annotated

from app.core.dependencies import get_current_user
from app.crud.classroom import (
    create_classroom,
    delete_classroom,
    get_classroom,
    list_classrooms,
    update_classroom,
)
from app.db.session import get_session
from app.schemas.classroom import ClassroomCreate, ClassroomRead, ClassroomUpdate
from app.schemas.errors import Error404Response

# Define the annotated dependency
SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/", response_model=ClassroomRead)
def create_classroom_endpoint(classroom: ClassroomCreate, session: SessionDep):
    new_classroom = ClassroomCreate(
        name=classroom.name,
        available_classes=classroom.available_classes,
    )
    return create_classroom(session, new_classroom)


@router.get(
    "/{classroom_id}",
    response_model=ClassroomRead,
    responses={
        404: {"description": "Classroom not found", "model": Error404Response},
    },
)
def get_classroom_endpoint(classroom_id: int, session: SessionDep):
    classroom = get_classroom(session, classroom_id)
    if not classroom:
        return JSONResponse(status_code=404, content={"message": "Classroom not found"})
    return classroom


@router.get("/", response_model=List[ClassroomRead])
def list_classrooms_endpoint(session: SessionDep):
    return list_classrooms(session)


@router.delete(
    "/{classroom_id}",
    response_model=dict,
    responses={
        404: {"description": "Classroom not found", "model": Error404Response},
    },
)
def delete_classroom_endpoint(classroom_id: int, session: SessionDep):
    success = delete_classroom(session, classroom_id)
    if not success:
        return JSONResponse(status_code=404, content={"message": "Classroom not found"})
    return {"message": "Classroom deleted successfully"}


@router.put("/{classroom_id}", response_model=ClassroomRead)
def update_classroom_endpoint(
    classroom_id: int,
    session: SessionDep,
    classroom_data: ClassroomUpdate,
):
    updated_classroom = update_classroom(session, classroom_id, classroom_data)
    if not updated_classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    return updated_classroom
