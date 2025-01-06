import logging
from collections import namedtuple
from dataclasses import dataclass
from itertools import groupby
from operator import attrgetter

from ortools.sat.python import cp_model

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


def convert_time_to_min(time: int):  # hhmm
    hours = time // 100
    minutes = time % 100
    total_minutes = hours * 60 + minutes
    return total_minutes


def minutes_to_time(total_minutes: int):
    # total_minutes = total_minutes % 1440  # Wrap around at 1440 minutes (24 hours)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return str(hours * 100 + minutes).zfill(4)


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


class printer(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(
        self,
        bool_variables: dict[tuple[int, TimeProf], cp_model.IntVar],
        interval_variables: dict[tuple[int, TimeProf], cp_model.IntervalVar],
        model,
        save_last: bool = True,
    ):
        super().__init__()
        self.bool_variables = bool_variables
        self.interval_variables = interval_variables
        self.count = 0
        self.model: cp_model.CpModel = model
        self.last_sol = list()
        self.save_last = save_last
        self.sol_list = list()

    def on_solution_callback(self):
        self.count += 1
        self.last_sol.clear()
        sol = []
        for k, v in self.bool_variables.items():
            if self.value(v):
                if self.save_last:
                    self.last_sol.append((k, v))
                    continue
                print(
                    k[0],
                    k[1].group,
                    k[1].day,
                    minutes_to_time(k[1].start),
                    minutes_to_time(k[1].end),
                    k[1].prof,
                    k[1].prefered,
                )
                sol.append(
                    [
                        k[0],
                        k[1].group,
                        k[1].day,
                        minutes_to_time(k[1].start),
                        minutes_to_time(k[1].end),
                        k[1].prof,
                        k[1].prefered,
                    ]
                )
        if len(sol) == 4:
            self.sol_list.append((sol, sum([x[-1] for x in sol])))


class ModelSolver:
    def __init__(self, data: dict[str, Course], num_solution: int = 50) -> None:
        self.data: dict[str, Course] = data
        self.num_solution = num_solution
        self.soloutins = []

    def solve(self) -> list[list[tuple[str, TimeProf, int]]]:
        self.soloutins.clear()
        # struct
        # prof:3 day:1 start:4
        model = cp_model.CpModel()
        # Model the problem
        interval_variables: dict[tuple[str, TimeProf], cp_model.IntervalVar] = {}
        bool_variables: dict[tuple[str, TimeProf], cp_model.IntVar] = {}
        bool_variables_prefered: list[cp_model.IntVar] = []
        # Creat all Variables
        for k, v in self.data.items():
            course_times = list()
            for time in v.times:
                bool_variables[(k, time)] = model.new_bool_var(
                    f"bool_course_{k}_day_{time.day}_start_{minutes_to_time(time.start)}_end_{minutes_to_time(time.end)}_prof_{time.prof}_prefered_{time.prefered}"
                )
                if time.prefered:
                    bool_variables_prefered.append(bool_variables[(k, time)])
                interval_variables[(k, time)] = model.NewOptionalIntervalVar(
                    start=int(str(time.day + 1) + str(time.start)),
                    size=time.end - time.start,
                    end=int(str(time.day + 1) + str(time.end)),
                    is_present=bool_variables[(k, time)],
                    name=f"bool_course_{k}_day_{time.day}_start_{minutes_to_time(time.start)}_end_{minutes_to_time(time.end)}_prof_{time.prof}_prefered_{time.prefered}",
                )
                course_times.append(bool_variables[(k, time)])
            model.add_exactly_one(course_times)

        # Creat Group constraints
        group_data: dict[int, list[Course]] = {
            group: list(items)
            for group, items in groupby(
                sorted(list(self.data.values()), key=attrgetter("group")),
                key=attrgetter("group"),
            )
        }
        for k, v in group_data.items():
            group_intervals = []
            for course in v:
                for time in course.times:
                    group_intervals.append(interval_variables[(course.id, time)])
            demands = [1] * len(group_intervals)
            model.add_cumulative(group_intervals, demands, 1)

        # Creat professor constraints
        professor_data: dict[str, list[tuple[TimeProf, str]]] = {}
        for prof, items in groupby(
            sorted(
                [
                    (time, course[0])
                    for course in self.data.items()
                    for time in course[1].times
                ],
                key=lambda x: x[0].prof,
            ),
            key=lambda x: x[0].prof,
        ):
            professor_data[prof] = list(items)
        for prof_id, val in professor_data.items():
            professor_intervals = []
            for time, coruse_id in val:
                professor_intervals.append(interval_variables[(coruse_id, time)])
            demands = [1] * len(professor_intervals)
            model.add_cumulative(professor_intervals, demands, 1)

        model.maximize(sum(bool_variables_prefered))
        solver = cp_model.CpSolver()
        # solver.parameters.enumerate_all_solutions = True
        # sol_print = printer(bool_variables, interval_variables, model)
        # sol_print = printer(bool_variables, interval_variables, model, save_last=False)

        for i in range(self.num_solution):
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
            last_sol = list()
            for (id, timeprof), variable in bool_variables.items():
                if solver.value(variable):
                    sol_vars.append(variable)
                    # TODO :Add score to it
                    last_sol.append((id, timeprof, 50))
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
            model.add(sum(sol_vars) <= len(sol_vars) - 1)
            print(solver.user_time)
            self.soloutins.append(last_sol)
        return self.soloutins


if __name__ == "__main__":
    from mock_data import MockData

    mock = MockData(num_courses=700, proffesor_cout=500,group_max=70,timeslot_per_course_min=5,timeslot_per_course_max=12)
    input_data = mock.generate_data()
    data = parse_courses(input_data)

    Mo = ModelSolver(data=data, num_solution=20)
    sols = Mo.solve()
    for i in sols:
        for j in i:
            print(
                j[0],
                j[1].group,
                j[1].day,
                minutes_to_time(j[1].start),
                minutes_to_time(j[1].end),
                j[1].prof,
                j[1].prefered,
            )
        print("\n\n\n")
