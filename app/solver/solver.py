# ruff: noqa: C408
import logging
from collections import namedtuple
from dataclasses import dataclass
from itertools import groupby
from operator import attrgetter

from ortools.sat.python import cp_model

from app.schemas.professors import ProfessorRead
from app.schemas.solver import CourceTimeSlots as SolverCourseTimeSlot
from app.schemas.solver import Courses as SolverCourse
from app.schemas.solver import SolverSettings, convert_time_to_min

# from data_min import COURSES
# from data_min2 import COURSES

logger = logging.getLogger()


class ModelSolver:
    def __init__(
        self,
        data: list[SolverCourse],
        settings: SolverSettings,
        professors: dict[int, ProfessorRead],
        debug:bool=False
    ) -> None:
        ids = set()
        for i in data:
            if i.id not in ids:
                ids.add(i.id)
            else:
                raise ValueError("There is a duplicate id among the courses")
        self.data: list[SolverCourse] = data
        self.settings: SolverSettings = settings
        self.soloutins: list[list[tuple[int, SolverCourseTimeSlot, int]]] = list()
        self.professors: dict[int, ProfessorRead] = professors

    def solve(self):  # noqa: C901
        self.soloutins.clear()
        model = cp_model.CpModel()
        # Model the problem
        # the actual time intervals for each course time slots, it is then linked to bool_variables
        courses_dict = {course.id: course for course in self.data}
        interval_variables: dict[
            tuple[int, SolverCourseTimeSlot], cp_model.IntervalVar
        ] = {}
        # basicly time slots that says what time slot is selected for the cours e
        bool_variables: dict[tuple[int, SolverCourseTimeSlot], cp_model.IntVar] = {}
        # list of time slots that are perefered
        bool_variables_prefered: list[cp_model.IntVar] = list()
        # Creat all Variables
        for course in self.data:
            course_times = list()
            if len(course.time_slots) == 0:
                raise ValueError(f"Course {course} dose not have any timeslot")
            # create the bool and intvars from the courses and add them to the list
            for time in course.time_slots:
                bool_variables[(course.id, time)] = model.new_bool_var(
                    name=f"bool_course_{course.id}_day_{time.day}_start_{time.start_time}_end_{time.end_time}_prof_{time.prof}_prefered_{time.prefered}"
                )
                if time.prefered:
                    bool_variables_prefered.append(bool_variables[(course.id, time)])
                model_start_time = convert_time_to_min(int(time.start_time))
                model_end_time = convert_time_to_min(int(time.end_time))
                interval_variables[(course.id, time)] = model.NewOptionalIntervalVar(
                    start=int(str(time.day + 1) + str(model_start_time).zfill(4)),
                    size=model_end_time - model_start_time,
                    end=int(str(time.day + 1) + str(model_end_time).zfill(4)),
                    is_present=bool_variables[(course.id, time)],
                    name=f"bool_course_{course.id}_day_{time.day}_start_{str(time.start_time)}_end_{str(time.end_time)}_prof_{time.prof}_prefered_{time.prefered}",
                )
                course_times.append(bool_variables[(course.id, time)])
            # select exactly 1 time per course‌ (basically you have to select a time for a course)
            model.add_exactly_one(course_times)
            if self.settings.debug:
                solver = cp_model.CpSolver()
                ans=solver.solve(model)
                if ans!=4:
                    raise ValueError(f"درس {course} باعث خرابی جواب میشود")
        # Creat Group constraints (only 1 class blonging to a group (group_id calculated by semester and major id) can happen at a time)
        group_data: dict[int, list[SolverCourse]] = {
            group: list(items)
            for group, items in groupby(
                sorted(self.data, key=attrgetter("group_id")),
                key=attrgetter("group_id"),
            )
        }
        for group_id in group_data.values():
            group_intervals = list()
            for course in group_id:
                for time in course.time_slots:
                    group_intervals.append(interval_variables[(course.id, time)])  # noqa: PERF401
            demands = [1] * len(group_intervals)
            model.add_cumulative(group_intervals, demands, 1)
            if self.settings.debug:
                solver = cp_model.CpSolver()
                ans=solver.solve(model)
                if ans!=4:
                    raise ValueError(f"گروه {group_id} باعت خرابی جواب میشود")
        # Creat professor constraints (a professor cant teach > 1 class at the same time)
        # tuple[solvercoursetimeslot,course_id]
        professors_data: dict[int, list[tuple[SolverCourseTimeSlot, int]]] = {}
        for prof, items in groupby(
            sorted(
                [
                    (time, course.id)
                    for course in self.data
                    for time in course.time_slots
                ],
                key=lambda x: x[0].prof,
            ),
            key=lambda x: x[0].prof,
        ):
            professors_data[prof] = list(items)
        for prof_id, val in professors_data.items():  # noqa: PERF102
            professor_intervals = list()
            for time, coruse_id in val:
                professor_intervals.append(interval_variables[(coruse_id, time)])
            demands = [1] * len(professor_intervals)
            model.add_cumulative(professor_intervals, demands, 1)
            if self.settings.debug:
                solver = cp_model.CpSolver()
                ans=solver.solve(model)
                if ans!=4:
                    raise ValueError(f"استاد با id {self.professors[prof_id]} باعث خرابی جواب میشود")
        # Min and max course hours for professor constraints, ensures is the professor has min max hourse > 0, that they are added to model constraints
        if self.settings.professor_min_max_time_limitation:
            for prof_id, val in professors_data.items():
                professor_data: ProfessorRead = self.professors[prof_id]
                prof_min_hour = professor_data.min_hour
                prof_max_hour = professor_data.max_hour
                if prof_max_hour == 0 and prof_min_hour == 0:
                    continue

                bool_vars = []
                hours = []
                for slot, course_id in val:
                    bool_vars.append(bool_variables[(course_id, slot)])
                    hours.append(courses_dict[course_id].calculated_hours)
                if prof_max_hour > 0:
                    model.add(
                        sum(bool_var * hour for bool_var, hour in zip(bool_vars, hours))
                        <= prof_max_hour * 100
                    )
                if prof_min_hour > 0:
                    model.add(
                        sum(bool_var * hour for bool_var, hour in zip(bool_vars, hours))
                        >= prof_min_hour * 100
                    )
                if self.settings.debug:
                    solver = cp_model.CpSolver()
                    ans=solver.solve(model)
                    if ans!=4:
                        raise ValueError(f"محدودیت ساعت برای استاد {professor_data} باعث خرابی جواب میشود")
        # Add constraints on maximum number on classes that need a spesicif classroom, like computer or architechture classrooms.
        if self.settings.classroom_limitation:
            classroom_data: dict[int, list[SolverCourse]] = {
                group: list(items)
                for group, items in groupby(
                    sorted(self.data, key=attrgetter("classroom_id")),
                    key=attrgetter("classroom_id"),
                )
            }
            for courses in classroom_data.values():
                classroom_intervals = list()
                max_classes = 0
                for course in courses:
                    max_classes = course.max_classes
                    for time in course.time_slots:
                        classroom_intervals.append(  # noqa: PERF401
                            interval_variables[(course.id, time)]
                        )
                demands = [1] * len(classroom_intervals)
                model.add_cumulative(classroom_intervals, demands, max_classes)
                if self.settings.debug:
                    solver = cp_model.CpSolver()
                    ans=solver.solve(model)
                    if ans!=4:
                        raise ValueError(f"محدودیت کلاس برای کلاس های {course.classroom_name} باعث خرابی جواب میشود") # type: ignore
        # maxumize for prefered time slots, maximize the perefered time by the professors
        model.maximize(sum(bool_variables_prefered))
        solver = cp_model.CpSolver()
        for i in range(self.settings.number_of_solutions):
            stat = solver.solve(model)
            if stat == cp_model.INFEASIBLE:
                logger.info("INFEASIBLE")
                break
            if stat == cp_model.MODEL_INVALID:
                logger.info("MODEL_INVALID")
            if stat == cp_model.UNKNOWN:
                logger.info("UNKNOWN")
                break
            # if stat in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            #     print("optimal,fes")
            sol_vars = list()
            # course id, selected time slot, score of this solution
            last_sol: list[tuple[int, SolverCourseTimeSlot, int]] = list()
            # append the solution to the list of solutions
            for (id, solver_timeslot), model_bool_variable in bool_variables.items():  # noqa: A001
                if solver.value(model_bool_variable):
                    sol_vars.append(model_bool_variable)
                    # TODO :Add score to it, 50 is just a placeholder
                    last_sol.append((id, solver_timeslot, 50))
            model.add(sum(sol_vars) <= len(sol_vars) - 1)
            print(solver.user_time)
            self.soloutins.append(last_sol)
        return self.soloutins


if __name__ == "__main__":
    pass
