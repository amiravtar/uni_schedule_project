from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session
from typing_extensions import (
    Annotated,  # Import Annotated for backward compatibility if needed
)

from app.crud.major import (
    create_major,
    delete_major,
    get_major,
    list_majors,
    update_major,
)
from app.db.session import get_session
from app.models import Major
from app.schemas.errors import Error404Response
from app.schemas.major import MajorCreate, MajorRead

# Define the annotated dependency
SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter()


@router.post("/", response_model=MajorRead)
def create_major_endpoint(major: MajorCreate, session: SessionDep):
    new_major = Major(name=major.name, semesters=major.semesters)
    return create_major(session, new_major)


@router.get(
    "/{major_id}",
    response_model=MajorRead,
    responses={
        404: {"description": "Major not found", "model": Error404Response},
    },
)
def get_major_endpoint(major_id: int, session: SessionDep):
    major = get_major(session, major_id)
    if not major:
        return JSONResponse(status_code=404, content={"message": "Major not found"})
    return major


@router.get("/", response_model=List[MajorRead])
def list_majors_endpoint(session: SessionDep):
    return list_majors(session)


@router.delete(
    "/{major_id}",
    response_model=dict,
    responses={
        404: {"description": "Major not found", "model": Error404Response},
    },
)
def delete_major_endpoint(major_id: int, session: SessionDep):
    success = delete_major(session, major_id)
    if not success:
        return JSONResponse(status_code=404, content={"message": "Major not found"})
    return {"message": "Major deleted successfully"}


@router.put("/{major_id}", response_model=MajorRead)
def update_major_endpoint(
    major_id: int,
    session: SessionDep,
    name: str | None = None,
    semesters: int | None = None,
):
    updated_major = update_major(session, major_id, name=name, semesters=semesters)
    if not updated_major:
        raise HTTPException(status_code=404, detail="Major not found")
    return updated_major
