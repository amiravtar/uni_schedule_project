# ruff: noqa: C408

from datetime import datetime, timedelta

from app.schemas.course import CourseRead
from app.schemas.professors import ProfessorRead, TimeSlot, Weekday
from app.schemas.solver import (
    CourceTimeSlots,
    SolverCourseSelectedDate,
    SolverResualt,
    SolverSolution,
    SolverSolutionCourse,
)
from app.schemas.solver import Courses as SolverSourses


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
    professor: ProfessorRead,
) -> list[CourceTimeSlots]:
    """Generates time slots of given duration within the specified time range."""
    slots: set[CourceTimeSlots] = set()
    current_time = start_time
    while current_time + duration <= end_time:
        next_time = current_time + duration
        slot = CourceTimeSlots(
            day=day.value,
            start_time=current_time.strftime("%H%M"),
            end_time=next_time.strftime("%H%M"),
            original_start=current_time.strftime("%H%M"),
            prof=professor.id,
            prefered=is_preferred,
        )
        slots.add(slot)
        current_time = next_time
    current_time = end_time
    while current_time - duration >= start_time:
        next_time = current_time - duration
        slot = CourceTimeSlots(
            day=day.value,
            start_time=next_time.strftime("%H%M"),
            end_time=current_time.strftime("%H%M"),
            original_start=next_time.strftime("%H%M"),
            prof=professor.id,
            prefered=is_preferred,
        )
        slots.add(slot)
        current_time = next_time
    time_slots = list(slots)
    return time_slots


def get_professor_slots(prof: ProfessorRead, duration: str) -> list[CourceTimeSlots]:
    """Returns the sum of all of its ranges in slots of specified duration."""
    duration_hours, duration_minutes = map(int, duration.split(":"))
    duration_delta = timedelta(hours=duration_hours, minutes=duration_minutes)
    all_slots = set()

    for time_slot in prof.time_slots:
        day, start_time, end_time = parse_time_range(time_slot)
        is_preferred = day in prof.preferred_days
        slots = generate_time_slots(
            day, start_time, end_time, duration_delta, is_preferred, professor=prof
        )
        all_slots.update(slots)

    return list(all_slots)


def parse_solver_output(
    sols: list[list[tuple[int, CourceTimeSlots, int]]],
    input_courses: list[SolverSourses],
    professors: dict[int, ProfessorRead],
) -> SolverResualt:
    solver_resualt: SolverResualt = SolverResualt(Solutions=list())
    for sol in sols:
        solver_solution: SolverSolution = SolverSolution(courses=list())
        for course_id, timeslot, score in sol:
            course: SolverSourses = next(
                (x for x in input_courses if x.id == course_id)
            )
            solver_sol_course = SolverSolutionCourse(
                **course.model_dump(exclude={"time_slots"}),
                selected_slot=SolverCourseSelectedDate(
                    day=timeslot.day,
                    start_time=timeslot.start_time,
                    end_time=timeslot.end_time,
                    professor_id=timeslot.prof,
                    professor_name=professors[timeslot.prof].full_name,
                    prefered=timeslot.prefered,
                ),
            )
            solver_solution.courses.append(solver_sol_course)
        solver_resualt.Solutions.append(solver_solution)
    return solver_resualt


def convert_course_read_list_to_solver_course_list(
    input_courses: list[CourseRead],
) -> list[SolverSourses]:
    """converts CoursesRead list to SolverCourses list"""
    solver_courses: list[SolverSourses] = []
    for course in input_courses:
        solver_course = SolverSourses(
            id=course.id,
            calculated_hours=int(course.calculated_hours * 100),
            duration=course.duration,
            major_id=course.major_id,
            classroom_id=course.classroom_id,
            title=course.title,
            units=course.units,
            semester=course.semester,
            max_classes=course.classroom.available_classes,  # type: ignore
            group_id=course.major_id * 10 + course.semester,
            time_slots=[],
            classroom_name=course.classroom.name,  # type: ignore
            major_name=course.major.name,  # type: ignore
        )
        for professor in course.professors:
            solver_course.time_slots.extend(
                get_professor_slots(professor, course.duration)
            )
        solver_courses.append(solver_course)
    return solver_courses
