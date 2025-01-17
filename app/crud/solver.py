from typing import List, Optional

from sqlalchemy.orm import Session
from sqlmodel import select

from app.models.solver import SolverResualt
from app.schemas.solver import SolverHistoryResualtCreate


def create_solver_resualt(
    session: Session, solver_resualt_data: SolverHistoryResualtCreate
) -> SolverResualt:
    solver_resualt = SolverResualt(**solver_resualt_data.model_dump())
    session.add(solver_resualt)
    session.commit()
    session.refresh(solver_resualt)
    return solver_resualt


def get_solver_resualt(
    session: Session, solver_resualt_id: int
) -> Optional[SolverResualt]:
    return session.get(SolverResualt, solver_resualt_id)


def list_solver_resualts(session: Session) -> List[SolverResualt]:
    query = select(SolverResualt).order_by(SolverResualt.created_at.desc())  # type: ignore
    return session.exec(query).all()  # type: ignore


def delete_solver_resualt(session: Session, solver_resualt_id: int) -> bool:
    solver_resualt = get_solver_resualt(session, solver_resualt_id)
    if not solver_resualt:
        return False

    session.delete(solver_resualt)
    session.commit()
    return True
