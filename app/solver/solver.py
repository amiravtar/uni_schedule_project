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
DURATION_PER_UNIT = 45


TimeProf = namedtuple(
    "TimeProf",
    ["day", "start", "end", "prof", "duration", "original_start", "group", "prefered"],
)


@dataclass
class Course:
    id: str
    group: int
    times: list[TimeProf]
    unit: int


def parse_courses(courses: list[tuple[str, list[str], int]]) -> dict[str, Course]:
    data: dict[str, Course] = dict()
    for i in courses:
        c = Course(id=i[0], group=i[2], times=list(), unit=3)
        time_slotes_set = set()
        for j in i[1]:
            day, start, end, prof, prefered = j.split(",")
            day = int(day)
            start = int(start)
            end = int(end)
            prefered = int(prefered)
            min_start = convert_time_to_min(start)
            min_end = convert_time_to_min(end)
            duration = end - start
            timeprof = TimeProf(
                day=day,
                start=min_start,
                end=min_end,
                prof=prof,
                duration=duration,
                original_start=start,
                group=i[2],
                prefered=prefered,
            )
            time_slotes_set.add(timeprof)
        if len(time_slotes_set) < len(i[1]):
            raise
        c.times.extend(time_slotes_set)
        data[c.id] = c
    return data


# unused
# class printer(cp_model.CpSolverSolutionCallback):
#     """Print intermediate solutions."""

#     def __init__(
#         self,
#         bool_variables: dict[tuple[int, TimeProf], cp_model.IntVar],
#         interval_variables: dict[tuple[int, TimeProf], cp_model.IntervalVar],
#         model,
#         save_last: bool = True,
#     ):
#         super().__init__()
#         self.bool_variables = bool_variables
#         self.interval_variables = interval_variables
#         self.count = 0
#         self.model: cp_model.CpModel = model
#         self.last_sol = list()
#         self.save_last = save_last
#         self.sol_list = list()

#     def on_solution_callback(self):
#         self.count += 1
#         self.last_sol.clear()
#         sol = list()
#         for k, v in self.bool_variables.items():
#             if self.value(v):
#                 if self.save_last:
#                     self.last_sol.append((k, v))
#                     continue
#                 print(
#                     k[0],
#                     k[1].group,
#                     k[1].day,
#                     minutes_to_time(k[1].start),
#                     minutes_to_time(k[1].end),
#                     k[1].prof,
#                     k[1].prefered,
#                 )
#                 sol.append(
#                     [
#                         k[0],
#                         k[1].group,
#                         k[1].day,
#                         minutes_to_time(k[1].start),
#                         minutes_to_time(k[1].end),
#                         k[1].prof,
#                         k[1].prefered,
#                     ]
#                 )
#         if len(sol) == 4:
#             self.sol_list.append((sol, sum([x[-1] for x in sol])))


class ModelSolver:
    def __init__(
        self,
        data: list[SolverCourse],
        settings: SolverSettings,
        professors: dict[int, ProfessorRead],
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
        interval_variables: dict[
            tuple[int, SolverCourseTimeSlot], cp_model.IntervalVar
        ] = {}
        # basicly time slots that says what time slot is selected for the course
        bool_variables: dict[tuple[int, SolverCourseTimeSlot], cp_model.IntVar] = {}
        # list of time slots that are perefered
        bool_variables_prefered: list[cp_model.IntVar] = list()
        # Creat all Variables
        for course in self.data:
            course_times = list()
            if len(course.time_slots) == 0:
                raise ValueError(f"Course {course} dose not have any timeslot")
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
            model.add_exactly_one(course_times)

        # Creat Group constraints (only 1 class blonging to a group (group_id calculated by semester and major id) can happen at a time)
        group_data: dict[int, list[SolverCourse]] = {
            group: list(items)
            for group, items in groupby(
                sorted(self.data, key=attrgetter("id")),
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

        # Min and max course hours for professor constraints
        if self.settings.professor_min_max_time_limitation:
            courses_dict = {course.id: course for course in self.data}
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

        # maxumize for prefered time slots
        model.maximize(sum(bool_variables_prefered))
        solver = cp_model.CpSolver()
        # solver.parameters.enumerate_all_solutions = True
        # sol_print = printer(bool_variables, interval_variables, model)
        # sol_print = printer(bool_variables, interval_variables, model, save_last=False)

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
            # for k, v in sol_print.last_sol:
            #     print(
            #         k[0],
            #         k[1].group,
            #         k[1].day,
            #         minutes_to_time(k[1].start),
            #         minutes_to_time(k[1].end),
            #         k[1].prof,
            #         k[1].prefered,
            #     )
            #     sol_vars.append(v)
            # remove the solution from the next possible solutions
            # by setting that, next solution cant have all the time slots of past solutions on, meaning at least 1 time slot has to differ
            model.add(sum(sol_vars) <= len(sol_vars) - 1)
            print(solver.user_time)
            self.soloutins.append(last_sol)
        return self.soloutins


if __name__ == "__main__":
    pass
    # from mock_data import MockData

    # mock = MockData(
    #     num_courses=700,
    #     proffesor_cout=500,
    #     group_max=70,
    #     timeslot_per_course_min=5,
    #     timeslot_per_course_max=12,
    # )
    # input_data = mock.generate_data()
    # data = parse_courses(input_data)

    # Mo = ModelSolver(data=data, num_solution=20)
    # sols = Mo.solve()
    # for i in sols:
    #     for j in i:
    #         print(
    #             j[0],
    #             j[1].group,
    #             j[1].day,
    #             minutes_to_time(j[1].start),
    #             minutes_to_time(j[1].end),
    #             j[1].prof,
    #             j[1].prefered,
    #         )
    #     print("\n\n\n")
