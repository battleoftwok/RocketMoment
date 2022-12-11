from dataclasses import dataclass, field
from datetime import timedelta
import matplotlib.pyplot as plt
import os


@dataclass
class ConstParams:

    """
    Константы, используемые в расчёте
    """

    gravity: float = 9.81
    m_alpha_z: float = -.0033
    m_delta_z: float = -.0025
    radius: float = 57.3
    s_wing: float = 5.34
    q: float = 1236.25
    b_a: float = 1.684
    n_x: float = -7.0
    var_part_weight: float = 1.3
    airplane_wight: float = 132.55
    R_la: float = field(default=0, init=False)
    R_jt: float = field(default=0, init=False)


CONST_PARAMS = ConstParams()
STEP = timedelta(milliseconds=1)


def plot(data: dict):
    abscissa = data["time [сек]"]
    colour = ["red", "blue", "green", "black", "purple"]
    params = ["epsilon", "omega", "alpha", "delta_р.в."]

    fig, axs = plt.subplots(len(params))

    for key, item in zip(params, range(len(params))):
        axs[item].plot(abscissa, data[key], colour[item])
        axs[item].set_title(key)

    plt.savefig(f"{os.path.abspath(os.path.curdir)}/fig.jpg")
    plt.show()


@dataclass
class Data:
    # todo: названия физических величин!
    cur_time_step: float = 0.0
    jt: float = 38.84185
    airplane_inertia: float = 110.134
    r_2: float = 0.0
    inertia_moment: float = jt + airplane_inertia
    angular_acceleration: float = 0.0
    angular_velocity: float = 0.0
    attack_angle: float = 0.0
    elevator_angle: float = 0.0
    airplane_moment: float = 0.0
    velocity: float = 0.0
    lp: float = 0.0
    rocket_moment: float = 0.0
    time: timedelta = field(default=timedelta(milliseconds=0))
    counter_start_rocket: int = 0
    cur_weight_rocket: float = 0
    full_weight: float = 50.0

    def __post_init__(self):
        CONST_PARAMS.R_la = (self.airplane_inertia / CONST_PARAMS.airplane_wight) ** .5
        CONST_PARAMS.R_jt = (self.jt / self.full_weight) ** .5

    def recalc_data(self, current_time: timedelta):
        self.time = current_time
        self.cur_time_step = current_time.total_seconds()
        self.r_2 = 0.0
        self.jt = self.calc_jt()
        self.airplane_inertia = self.calc_airplane_inertia()
        self.inertia_moment = self.jt + self.airplane_inertia
        self.angular_acceleration += self.calc_angular_acceleration()
        self.angular_velocity += self.calc_angular_velocity()
        self.attack_angle += self.calc_attack_angle()
        self.elevator_angle += self.calc_elevator_angle()
        self.airplane_moment += self.calc_airplane_moment()
        self.velocity += 0
        self.lp += 0
        self.rocket_moment = 0

    def calc_airplane_inertia(self):
        return CONST_PARAMS.R_la ** 2 * (CONST_PARAMS.airplane_wight - self.counter_start_rocket *
                                         (self.cur_weight_rocket + CONST_PARAMS.var_part_weight))

    def calc_jt(self):
        return CONST_PARAMS.R_jt ** 2 * (self.full_weight - self.counter_start_rocket *
                                         (self.cur_weight_rocket + CONST_PARAMS.var_part_weight))

    def calc_airplane_moment(self) -> float:
        return self.rocket_moment + \
            (self.attack_angle * CONST_PARAMS.m_alpha_z *
             CONST_PARAMS.s_wing * CONST_PARAMS.q * CONST_PARAMS.b_a) / CONST_PARAMS.gravity + \
            (self.elevator_angle * CONST_PARAMS.m_delta_z *
             CONST_PARAMS.s_wing * CONST_PARAMS.q * CONST_PARAMS.b_a) / CONST_PARAMS.gravity

    def calc_elevator_angle(self) -> float:
        return - CONST_PARAMS.m_alpha_z * self.attack_angle / CONST_PARAMS.m_delta_z

    def calc_attack_angle(self) -> float:
        return self.attack_angle + self.angular_velocity * STEP.total_seconds()

    def calc_angular_acceleration(self) -> float:
        return self.airplane_moment * CONST_PARAMS.radius * CONST_PARAMS.gravity / self.inertia_moment

    def calc_angular_velocity(self) -> float:
        return self.angular_velocity + self.angular_velocity * STEP.total_seconds()


@dataclass(repr=True)
class Rocket:
    time_start: timedelta
    flight_duration: timedelta
    weight: float = 15

    # todo: по какому принципу происходит изменение coord_x и coord_y?
    coord_x = [0.055, 0.138, 0.221, 0.304, 0.387, 0.47,
               0.553, 0.636, 0.719, 0.802, 0.885, 0.968, 1.051,
               1.134, 1.217, 1.3]

    coord_y = 0.152

    def consider_moment(self, calc_params: Data, current_time: timedelta):

        if self.time_start == current_time:
            calc_params.cur_weight_rocket = self.weight

        time_diff = current_time - self.time_start
        calc_params.r_2 = self.coord_y ** 2 + self.coord_x[int(1000 * time_diff.total_seconds())] ** 2
        calc_params.jt = (calc_data.full_weight - calc_data.counter_start_rocket *
                          (CONST_PARAMS.var_part_weight + self.weight)) * calc_params.r_2
        calc_params.inertia_moment = calc_params.jt + calc_params.airplane_inertia

        if self.time_start + self.flight_duration == current_time:
            calc_params.counter_start_rocket += 1


if __name__ == '__main__':

    rockets = [
        Rocket(timedelta(seconds=4), timedelta(milliseconds=15), weight=15),
        Rocket(timedelta(seconds=8), timedelta(milliseconds=15), weight=15)
    ]

    flight_time = timedelta(seconds=10)
    current = timedelta(milliseconds=0)

    calc_data = Data()

    while current <= flight_time:

        calc_data.recalc_data(current)

        for rocket in rockets:
            if rocket.time_start <= current <= rocket.time_start + rocket.flight_duration:
                rocket.consider_moment(calc_data, current)
                print(111)

        print(calc_data.jt, calc_data.airplane_inertia, calc_data.inertia_moment)
        current = current + STEP
