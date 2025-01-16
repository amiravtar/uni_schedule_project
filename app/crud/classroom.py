from typing import List, Optional

from sqlalchemy.orm import Session
from sqlmodel import select

from app.models.classroom import Classroom
from app.schemas.classroom import ClassroomCreate, ClassroomUpdate


def create_classroom(session: Session, classroom_data: ClassroomCreate) -> Classroom:
    classroom = Classroom(**classroom_data.model_dump())
    session.add(classroom)
    session.commit()
    session.refresh(classroom)
    return classroom


def get_classroom(session: Session, classroom_id: int) -> Optional[Classroom]:
    return session.get(Classroom, classroom_id)


def list_classrooms(session: Session) -> List[Classroom]:
    query = select(Classroom).order_by(Classroom.id.desc())  # type: ignore
    return session.exec(query).all()  # type: ignore


def update_classroom(
    session: Session, classroom_id: int, update_data: ClassroomUpdate
) -> Optional[Classroom]:
    classroom = get_classroom(session, classroom_id)
    if not classroom:
        return None

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(classroom, key, value)

    session.commit()
    session.refresh(classroom)
    return classroom


def delete_classroom(session: Session, classroom_id: int) -> bool:
    classroom = get_classroom(session, classroom_id)
    if not classroom:
        return False

    session.delete(classroom)
    session.commit()
    return True
