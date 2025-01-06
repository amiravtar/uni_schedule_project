import random


class MockData:
    def __init__(
        self,
        num_courses=5,
        timeslot_per_course_min=3,
        timeslot_per_course_max=10,
        prof_per_course_max=4,
        prof_per_course_min=2,
        proffesor_cout=10,
        group_min=1,
        group_max=4,
    ) -> None:
        self.num_courses = num_courses
        self.timeslot_per_course_min = timeslot_per_course_min
        self.timeslot_per_course_max = timeslot_per_course_max
        self.prof_per_course_max = prof_per_course_max
        self.prof_per_course_min = prof_per_course_min
        self.group_min = group_min
        self.group_max = group_max

        self.days = range(7)
        self.professors = [str(x) for x in range(10, 10 + (proffesor_cout * 10), 10)]

    def generate_random_time(self):
        start_hour = random.randint(8, 15)
        start_minute = random.choice([0, 30])
        start_time = f"{start_hour:02}{start_minute:02}"

        end_hour = start_hour
        end_minute = start_minute + 90
        if end_minute >= 60:
            end_hour += 1
            end_minute -= 60
        end_time = f"{end_hour:02}{end_minute:02}"

        return start_time, end_time

    def generate_timeslots(self,num_timeslots, selected_professors):
        timeslots = set()
        while len(timeslots)<num_timeslots:
            day = random.choice(self.days)
            start_time, end_time = self.generate_random_time()
            professor_id = random.choice(selected_professors)
            is_preferred = random.choice([0, 1])
            timeslots.add(f"{day},{start_time},{end_time},{professor_id},{is_preferred}")
        return timeslots

    def generate_courses(self, num_courses):
        courses = []
        for _ in range(num_courses):
            course_id = str(random.randint(100, 999))
            num_timeslots = random.randint(self.timeslot_per_course_min, self.timeslot_per_course_max)
            num_professors = random.randint(self.prof_per_course_min, self.prof_per_course_max)
            selected_professors = random.sample(self.professors, num_professors)
            timeslots = list(self.generate_timeslots(num_timeslots, selected_professors))
            group = random.randint(self.group_min, self.group_max)
            courses.append((course_id, timeslots, group))
        return courses

    def generate_data(self):
        return list(self.generate_courses(self.num_courses))
