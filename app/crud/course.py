from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.crud.classroom import get_classroom
from app.crud.major import get_major
from app.models.course import Course, CourseProfessorLink
from app.schemas.course import CourseCreate, CourseUpdate


def create_course(db: Session, course_data: CourseCreate) -> Course:
    major = get_major(db, course_data.major_id)
    if not major:
        raise HTTPException(status_code=404, detail="major not found")
    classroom = get_classroom(db, course_data.classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="classroom not found")
    # Create the course
    course = Course(
        title=course_data.title,
        units=course_data.units,
        duration=course_data.duration,
        semester=course_data.semester,
        calculated_hours=course_data.calculated_hours,
        major_id=course_data.major_id,
        classroom_id=course_data.classroom_id,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    # Handle the many-to-many relationship with professors
    for professor_id in course_data.professor_ids:
        link = CourseProfessorLink(course_id=course.id, professor_id=professor_id)
        db.add(link)
    db.commit()

    return course


def get_course(db: Session, course_id: int) -> Optional[Course]:
    return db.get(Course, course_id)


def list_courses(db: Session) -> List[Course]:
    query = (
        select(Course)
        .options(
            selectinload(
                Course.professors  # type: ignore
            ),  # Adjust this line based on your actual relationship
            selectinload(Course.major),  # type: ignore
            selectinload(Course.classroom),  # type: ignore
        )
        .order_by(Course.id.desc())  # type: ignore
    )
    return db.exec(query).all()  # type: ignore


def update_course(
    db: Session, course_id: int, update_data: CourseUpdate
) -> Optional[Course]:
    # Get the course
    course = get_course(db, course_id)
    if not course:
        return None

    if update_data.major_id is not None:
        major = get_major(db, update_data.major_id)
        if not major:
            raise HTTPException(status_code=404, detail="major not found")
    if update_data.classroom_id is not None:
        classroom = get_classroom(db, update_data.classroom_id)
        if not classroom:
            raise HTTPException(status_code=404, detail="classroom not found")
    # Update the course fields
    for key, value in update_data.model_dump(exclude_unset=True).items():
        if key != "professor_ids":  # Skip professor updates for now
            setattr(course, key, value)

    # Update professors if provided
    if update_data.professor_ids is not None:
        # Remove existing professor links
        db.query(CourseProfessorLink).where(
            CourseProfessorLink.course_id == course_id  # type: ignore
        ).delete(synchronize_session=False)

        # Add new professor links
        for professor_id in update_data.professor_ids:
            link = CourseProfessorLink(course_id=course.id, professor_id=professor_id)
            db.add(link)

    db.commit()
    db.refresh(course)
    return course


def delete_course(db: Session, course_id: int) -> bool:
    # Get the course
    course = db.query(Course).where(Course.id == course_id).first()  # type: ignore
    if not course:
        return False

    # Delete professor links first (to maintain referential integrity)
    db.query(CourseProfessorLink).filter(
        CourseProfessorLink.course_id == course_id  # type: ignore
    ).delete()

    # Delete the course
    db.delete(course)
    db.commit()
    return True
