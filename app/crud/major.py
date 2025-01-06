from typing import List, Optional

from sqlmodel import Session, select

from app.models import Major


def create_major(session: Session, major_data: Major) -> Major:
    session.add(major_data)
    session.commit()
    session.refresh(major_data)
    return major_data


def get_major(session: Session, major_id: int) -> Optional[Major]:
    return session.get(Major, major_id)


def list_majors(session: Session) -> List[Major]:
    query = select(Major)
    return session.exec(query).all()


def delete_major(session: Session, major_id: int) -> bool:
    major = session.get(Major, major_id)
    if major:
        session.delete(major)
        session.commit()
        return True
    return False


def update_major(
    session: Session,
    major_id: int,
    name: Optional[str] = None,
    semesters: Optional[int] = None,
) -> Optional[Major]:
    major = session.get(Major, major_id)
    if not major:
        return None
    if name is not None:
        major.name = name
    if semesters is not None:
        major.semesters = semesters
    session.add(major)
    session.commit()
    session.refresh(major)
    return major
