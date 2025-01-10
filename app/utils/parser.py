from datetime import datetime, timedelta

from app.schemas.course import CourseRead
from app.schemas.professors import ProfessorRead, TimeSlot, Weekday
from app.schemas.solver import Cources as SolverSourses
from app.schemas.solver import CourceTimeSlots
from schema.json import ModelResualt, Professor, ResualtCourse, ResualtDict, RootSchema
from solver.solver import TimeProf, minutes_to_time


def parse_time_range(time_slot: TimeSlot) -> tuple[Weekday, datetime, datetime]:
    """Parses a time slot string into day, start time, and end time."""
    day: int = time_slot.day
    start_str = time_slot.start_time
    end_str = time_slot.end_time
    start_time = datetime.strptime(start_str, "%H:%M")
    end_time = datetime.strptime(end_str, "%H:%M")
    return day, start_time, end_time


def generate_time_slots(
    day: Weekday,
    start_time: datetime,
    end_time: datetime,
    duration: timedelta,
    is_preferred: bool,
    proff_id: int,
) -> list[str]:
    """Generates time slots of given duration within the specified time range."""
    slots = []
    current_time = start_time
    while current_time + duration <= end_time:
        next_time = current_time + duration
        slot = f"{day.value},{current_time.strftime('%H%M')},{next_time.strftime('%H%M')},{proff_id},{int(is_preferred)}"
        slots.append(slot)
        current_time = next_time
    return slots


def get_professor_slots(prof: ProfessorRead, duration: str) -> list[CourceTimeSlots]:
    """Returns the sum of all of its ranges in slots of specified duration."""
    duration_hours, duration_minutes = map(int, duration.split(":"))
    duration_delta = timedelta(hours=duration_hours, minutes=duration_minutes)
    all_slots = []

    for time_slot in prof.time_slots:
        day, start_time, end_time = parse_time_range(time_slot)
        is_preferred = day in prof.preferred_days
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


def convert_course_read_list_to_solver_course_list(
    input_courses: list[CourseRead],
) -> list[SolverSourses]:
    """converts CoursesRead list to SolverCourses list"""
    solver_courses: list[SolverSourses] = []
    for course in input_courses:
        solver_course = SolverSourses(
            id=course.id,
            calculated_hours=course.calculated_hours,
            duration=course.duration,
            major_id=course.major_id,
            classroom_id=course.classroom_id,
            title=course.title,
            units=course.units,
            semester=course.semester,
            max_classes=course.classroom.available_classes,  # type: ignore
            group_id=course.major_id * 10 + course.semester,
            time_slots=[],
        )
        for professor in course.professors:
            solver_course.time_slots.extend(
                get_professor_slots(professor, course.duration)
            )
        solver_courses.append(solver_course)
    return solver_courses
