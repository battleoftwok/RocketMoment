from dataclasses import dataclass, field
from datetime import timedelta

SEPARATOR = ";"


@dataclass
class ConstParams:

    """
    Константы, используемые в расчёте
    """

    gravity: float = 9.81
    m_alpha_z: float = -0.0033
    m_delta_z: float = -0.0015
    radius: float = 57.3
    wing_area: float = 5.34
    q: float = 1236.25
    b_a: float = 1.684
    n_x: float = -7.0
    var_part_weight: float = 1.3
    MPADS_weight: float = 50  # MPADS - Man-portable air-defense systems (ПЗРК)
    airplane_weight: float = 132.55


@dataclass
class Data:
    rockets_set: list = field(repr=False)
    millisecond: float = 0
    time_point: timedelta = timedelta(seconds=0)
    rocket_launch_counter: int = 0
    airplane_moment_inertia_radius: float = 0.911529735
    airplane_moment_inertia: float = 0
    tube_moment_inertia_radius: float = 0.881383571
    rocket_moment_inertia: float = 0
    general_moment_inertia: float = 0
    airplane_acceleration: float = 0
    airplane_velocity: float = 0
    airplane_attack_angle: float = 4.0
    elevator_angle: float = 0
    rocket_velocity: float = 0
    rocket_way: float = 0
    rocket_power: float = 0
    rocket_moment: float = 0
    general_moment: float = 0

    def recalc_data(self, time_point: timedelta):
        self.time_point = time_point
        self.millisecond = 1000 * self.time_point.total_seconds()
        self.airplane_moment_inertia_radius = 0.911529735
        self.airplane_moment_inertia = self.calc_airplane_moment_inertia()
        self.tube_moment_inertia_radius = 0.881383571
        self.rocket_moment_inertia = self.calc_rocket_moment_inertia()
        self.general_moment_inertia = self.airplane_moment_inertia + self.rocket_moment_inertia
        self.airplane_acceleration = self.calc_airplane_acceleration()
        self.airplane_velocity = self.calc_airplane_velocity()
        self.airplane_attack_angle += self.calc_airplane_attack_angle()
        self.elevator_angle = self.calc_elevator_angle()
        self.rocket_velocity = 0
        self.rocket_way = 0
        self.rocket_power = 0
        self.rocket_moment = 0
        self.general_moment = self.calc_general_moment()

    def calc_airplane_moment_inertia(self):
        return (self.airplane_moment_inertia_radius ** 2) *\
            (CONST_PARAMS.airplane_weight - self.rocket_launch_counter *
             (CONST_PARAMS.var_part_weight + self.rockets_set[self.rocket_launch_counter - 1].weight))

    def calc_rocket_moment_inertia(self):
        return (self.tube_moment_inertia_radius ** 2) * \
            (CONST_PARAMS.MPADS_weight - self.rocket_launch_counter *
             (CONST_PARAMS.var_part_weight + self.rockets_set[self.rocket_launch_counter - 1].weight))

    def calc_airplane_acceleration(self):
        return (57.3 * self.general_moment * CONST_PARAMS.gravity) / self.general_moment_inertia

    def calc_airplane_velocity(self):
        return self.airplane_acceleration * STEP.total_seconds()

    def calc_airplane_attack_angle(self):
        return self.airplane_velocity * STEP.total_seconds()

    def calc_elevator_angle(self):
        return - CONST_PARAMS.m_alpha_z * self.airplane_attack_angle / CONST_PARAMS.m_delta_z

    def calc_general_moment(self):
        return self.rocket_moment + \
               self.airplane_attack_angle * CONST_PARAMS.m_alpha_z * (CONST_PARAMS.q * CONST_PARAMS.wing_area *
                                                                      CONST_PARAMS.b_a / CONST_PARAMS.gravity) + \
               self.elevator_angle * CONST_PARAMS.m_delta_z * (CONST_PARAMS.q * CONST_PARAMS.wing_area *
                                                               CONST_PARAMS.b_a / CONST_PARAMS.gravity)


@dataclass(repr=True)
class Rocket:
    coord_x: list
    coord_y: float
    time_start: timedelta
    flight_duration: timedelta = timedelta(milliseconds=15)
    weight: float = 15

    def consider_moment(self, cur_data: Data, time: timedelta):

        if time == self.time_start:
            cur_data.rocket_way = 0
            cur_data.rocket_velocity = 0
            cur_data.rocket_way = 0
            cur_data.airplane_velocity = 0
        else:
            cur_data.rocket_velocity += CONST_PARAMS.n_x * CONST_PARAMS.gravity * STEP.total_seconds()
            cur_data.rocket_way += cur_data.rocket_velocity * STEP.total_seconds()

        cur_data.time_point = time
        cur_data.millisecond = 1000 * cur_data.time_point.total_seconds()
        time_diff = time - self.time_start
        cur_data.tube_moment_inertia_radius = self.coord_y ** 2 + self.coord_x[int(1000 * time_diff.total_seconds())] ** 2
        cur_data.rocket_moment_inertia = cur_data.tube_moment_inertia_radius * CONST_PARAMS.MPADS_weight
        cur_data.airplane_moment_inertia = cur_data.calc_airplane_moment_inertia()
        cur_data.airplane_acceleration = cur_data.calc_airplane_acceleration()
        cur_data.general_moment_inertia = cur_data.airplane_moment_inertia + cur_data.rocket_moment_inertia
        cur_data.airplane_velocity += cur_data.calc_airplane_velocity()
        cur_data.airplane_attack_angle += cur_data.calc_airplane_attack_angle()
        cur_data.elevator_angle = cur_data.calc_elevator_angle()
        cur_data.rocket_power = (CONST_PARAMS.var_part_weight + self.weight) * CONST_PARAMS.gravity
        cur_data.rocket_moment = cur_data.rocket_way * cur_data.rocket_power
        cur_data.general_moment = cur_data.calc_general_moment()

        if time == self.flight_duration + self.time_start:
            cur_data.rocket_launch_counter += 1


if __name__ == '__main__':

    CONST_PARAMS = ConstParams()

    rockets = [
        Rocket(coord_x=[0.055, 0.138, 0.221, 0.304, 0.387, 0.47,
                        0.553, 0.636, 0.719, 0.802, 0.885, 0.968,
                        1.051, 1.134, 1.217, 1.3],
               coord_y=.152,
               time_start=timedelta(milliseconds=5)),

        Rocket(coord_x=[0.075, 0.148, 0.221, 0.294, 0.367, 0.44,
                        0.513, 0.586, 0.659, 0.732, 0.805, 0.878,
                        0.951, 1.024, 1.097, 1.17],
               coord_y=.099,
               time_start=timedelta(milliseconds=30))
    ]

    flight_time = timedelta(seconds=10)
    current = timedelta(milliseconds=0)
    STEP = timedelta(milliseconds=1)

    data = Data(rockets)
    data.recalc_data(timedelta(seconds=0))

    with open("result.csv", "w", encoding="utf-8") as file:

        print(SEPARATOR.join(map(str, data.__dict__.keys())).replace("_", " "), file=file)

        while current <= flight_time:

            flag = [rocket for rocket in rockets if
                    rocket.time_start <= current <= rocket.flight_duration + rocket.time_start]

            if bool(flag) is True:
                flag[0].consider_moment(data, current)
            else:
                data.recalc_data(current)

            print(SEPARATOR.join(map(str, data.__dict__.values())), file=file)
            current = current + STEP
