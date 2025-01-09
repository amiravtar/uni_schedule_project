from typing import List, Optional

from fastapi import HTTPException
from sqlmodel import Session, select

from app.crud.major import get_major
from app.models.professor import Professor
from app.schemas.professors import ProfessorCreate, ProfessorUpdate


def create_professor(session: Session, professor_data: ProfessorCreate) -> Professor:
    major = get_major(session, professor_data.major_id)
    if not major:
        raise HTTPException(status_code=404, detail="major not found")
    professor = Professor(**professor_data.model_dump())
    session.add(professor)
    session.commit()
    session.refresh(professor)
    return professor


def get_professor(session: Session, professor_id: int) -> Optional[Professor]:
    return session.get(Professor, professor_id)


def list_professors(session: Session) -> List[Professor]:
    query = select(Professor)
    return session.exec(query).all()  # type: ignore


def update_professor(
    session: Session, professor_id: int, update_data: ProfessorUpdate
) -> Optional[Professor]:
    professor = get_professor(session, professor_id)
    if not professor:
        return None
    if update_data.major_id is not None:
        major = get_major(session, update_data.major_id)
        if not major:
            raise HTTPException(status_code=404, detail="major not found")
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(professor, key, value)

    session.commit()
    session.refresh(professor)
    return professor


def delete_professor(session: Session, professor_id: int) -> bool:
    professor = get_professor(session, professor_id)
    if not professor:
        return False

    session.delete(professor)
    session.commit()
    return True
