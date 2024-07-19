from dataclasses import dataclass, field


@dataclass
class SolverCourse:
    id: int
    semister: int
    slots: list[str] = field(
        default_factory=list
    )  # "0,0800,0930,100,0|1", day start end proff is_prefered_day