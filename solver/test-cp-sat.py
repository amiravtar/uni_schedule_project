from ortools.sat.python import cp_model
from dataclasses import dataclass
from collections import namedtuple
from itertools import groupby
from operator import attrgetter

# from data_min import COURSES
from data_2 import COURSES

DURATION_PER_UNIT = 45


TimeProf = namedtuple(
    "TimeProf", ["day", "start", "end", "prof", "duration", "original_start", "group"]
)


@dataclass
class Course:
    id: int
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


def parse_courses(courses: list[tuple[int, list[str], int]]) -> dict[int, Course]:
    data: dict[int, Course] = dict()
    for i in courses:
        c = Course(id=i[0], group=i[2], times=list(), unit=3)
        for j in i[1]:
            day, start, end, prof = map(int, j.split(","))
            min_start = convert_time_to_min(start)
            min_end = convert_time_to_min(end)
            duration = end - start
            c.times.append(
                TimeProf(
                    day=day,
                    start=min_start,
                    end=min_end,
                    prof=prof,
                    duration=duration,
                    original_start=start,
                    group=i[2],
                )
            )
        data[c.id] = c
    return data


data = parse_courses(COURSES)


class printer(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(
        self,
        bool_variables: dict[tuple[int, TimeProf], cp_model.IntVar],
        interval_variables: dict[tuple[int, TimeProf], cp_model.IntervalVar],
    ):
        super().__init__()
        self.bool_variables = bool_variables
        self.interval_variables = interval_variables
        self.count = 0

    def on_solution_callback(self):
        self.count += 1
        # for k, v in self.bool_variables.items():
        #     if self.value(v):
        #         print(
        #             k[0],
        #             k[1].group,
        #             k[1].day,
        #             minutes_to_time(k[1].start),
        #             minutes_to_time(k[1].end),
        #             k[1].prof,
        # print(self.count)
        #         )
        # print("\n\n\n")


# struct
# prof:3 day:1 start:4
model = cp_model.CpModel()
# Model the problem
interval_variables: dict[tuple[int, TimeProf], cp_model.IntervalVar] = {}
bool_variables: dict[tuple[int, TimeProf], cp_model.IntVar] = {}
# Creat all Variables
for k, v in data.items():
    course_times = []
    for time in v.times:
        bool_variables[(k, time)] = model.new_bool_var(
            f"bool_course_{k}_day_{time.day}_start_{time.start}_end_{time.end}_prof_{time.prof}"
        )
        interval_variables[(k, time)] = model.NewOptionalIntervalVar(
            start=int(str(time.day + 1) + str(time.start)),
            size=time.end - time.start,
            end=int(str(time.day + 1) + str(time.end)),
            is_present=bool_variables[(k, time)],
            name=f"bool_course_{k}_day_{time.day}_start_{time.start}_end_{time.end}_prof_{time.prof}",
        )
        course_times.append(bool_variables[(k, time)])
    model.add_exactly_one(course_times)


# Creat Group constraints
group_data: dict[int, list[Course]] = {
    group: list(items)
    for group, items in groupby(
        sorted(list(data.values()), key=attrgetter("group")), key=attrgetter("group")
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
professor_data: dict[int, list[tuple[TimeProf, int]]] = {}
for prof, items in groupby(
    sorted(
        [(time, course[0]) for course in data.items() for time in course[1].times],
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


solver = cp_model.CpSolver()
# Enumerate all solutions.
solver.parameters.enumerate_all_solutions = True
sol_print = printer(bool_variables, interval_variables)
solver.solve(model, sol_print)
print(solver.user_time)
print(solver.wall_time)
print(sol_print.count)