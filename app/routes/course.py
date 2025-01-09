from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session
from typing_extensions import Annotated

from app.core.dependencies import get_current_user
from app.crud.course import (
    create_course,
    delete_course,
    get_course,
    list_courses,
    update_course,
)
from app.db.session import get_session
from app.schemas.course import CourseCreate, CourseRead, CourseUpdate
from app.schemas.errors import Error404Response

# Define the annotated dependency
SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/", response_model=CourseRead)
def create_course_endpoint(course_data: CourseCreate, session: SessionDep):
    return create_course(session, course_data)


@router.get(
    "/{course_id}",
    response_model=CourseRead,
    responses={
        404: {"description": "Course not found", "model": Error404Response},
    },
)
def get_course_endpoint(course_id: int, session: SessionDep):
    course = get_course(session, course_id)
    if not course:
        return JSONResponse(status_code=404, content={"message": "Course not found"})
    return course


@router.get("/", response_model=List[CourseRead])
def list_courses_endpoint(session: SessionDep):
    return list_courses(session)


@router.put("/{course_id}", response_model=CourseRead)
def update_course_endpoint(
    course_id: int,
    session: SessionDep,
    course_data: CourseUpdate,
):
    updated_course = update_course(session, course_id, course_data)
    if not updated_course:
        raise HTTPException(status_code=404, detail="Course not found")
    return updated_course


@router.delete(
    "/{course_id}",
    response_model=dict,
    responses={
        404: {"description": "Course not found", "model": Error404Response},
    },
)
def delete_course_endpoint(course_id: int, session: SessionDep):
    success = delete_course(session, course_id)
    if not success:
        return JSONResponse(status_code=404, content={"message": "Course not found"})
    return {"message": "Course deleted successfully"}
