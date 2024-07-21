from schema.json import RootSchema, Professor, ModelResualt, ResualtCourse, ResualtDict
from schema.solver_schema import SolverCourse

from datetime import datetime, timedelta
from solver.solver import TimeProf, minutes_to_time


def parse_time_range(time_range: str) -> tuple[int, datetime, datetime]:
    """Parses a time range string into day, start time, and end time."""
    day, start_str, end_str = time_range.split(":")
    day = int(day)
    start_time = datetime.strptime(start_str, "%H%M")
    end_time = datetime.strptime(end_str, "%H%M")
    return day, start_time, end_time


def generate_time_slots(
    day: int,
    start_time: datetime,
    end_time: datetime,
    duration: timedelta,
    is_preferred: bool,
    proff_id: str,
) -> list[str]:
    """Generates time slots of given duration within the specified time range."""
    slots = []
    current_time = start_time
    while current_time + duration <= end_time:
        next_time = current_time + duration
        slot = f"{day},{current_time.strftime('%H%M')},{next_time.strftime('%H%M')},{proff_id},{int(is_preferred)}"
        slots.append(slot)
        current_time = next_time
    return slots


def get_professor_slots(prof: Professor, duration: str) -> list[str]:
    """Returns the sum of all of its ranges in slots of specified duration."""
    duration_hours, duration_minutes = int(duration[:2]), int(duration[2:])
    duration_delta = timedelta(hours=duration_hours, minutes=duration_minutes)
    all_slots = []

    for day_range in prof.days:
        day, start_time, end_time = parse_time_range(day_range)
        is_preferred = day in prof.pref_days
        slots = generate_time_slots(
            day, start_time, end_time, duration_delta, is_preferred, proff_id=prof.id
        )
        all_slots.extend(slots)

    return all_slots


def convert_model_resualt_to_json(
    sols: list[list[tuple[str, TimeProf, int]]], parsed_json_data: RootSchema
) -> ModelResualt:
    resualt = ModelResualt(resualts=list())
    for i in sols:
        sol_coruses = list()
        for id, timeslot, score in i:
            for course in parsed_json_data.data.courses:
                if not course.id == id:
                    continue
                resualt_course = ResualtCourse(
                    id=id,
                    # name=course.name,
                    # units=course.units,
                    # duration=course.duration,
                    # semister=int(timeslot.group),
                    day=int(timeslot.day),
                    start=str(minutes_to_time(timeslot.start)),
                    end=str(minutes_to_time(timeslot.end)),
                    professor_id=str(timeslot.prof),
                    is_prefered_time=bool(timeslot.prefered),
                )
                sol_coruses.append(resualt_course)
        resualt.resualts.append(ResualtDict(score=score, courses=sol_coruses))
    return resualt


def convert_json_schema_to_model_data(
    data: RootSchema,
) -> list[tuple[str, list[str], int]]:
    """converts incommig json(with root schema) data to solver data input schema

    [(
        101,
        [
            "0,0800,0930,100,1",
            "1,1500,1630,200,1",
        ],
        10,
    ),
    (
        102,
        [
            "0,0800,0930,100,0",
            "0,0930,1100,100,0",
            "0,1300,1430,100,0",
            "2,1500,1630,200,1",
        ],
        10,
    )]

    :param data: _description_
    :type data: RootSchema
    """
    solver_data: list[tuple[str, list[str], int]] = []
    for course in data.data.courses:
        solver_c = SolverCourse(id=course.id, semister=course.semister)
        for proff_id in course.professors:
            for proffesor in data.data.professors:
                if not proffesor.id == proff_id:
                    continue
                solver_c.slots.extend(get_professor_slots(proffesor, course.duration))
        solver_data.append((solver_c.id, solver_c.slots, solver_c.semister))
    return solver_data
