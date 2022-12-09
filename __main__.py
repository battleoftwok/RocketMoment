from dataclasses import dataclass
from datetime import timedelta
import matplotlib.pyplot as plt


@dataclass
class ConstParams:
    gravity: float = 9.81
    m_alpha_z: float = -.0033
    m_delta_z: float = -.0025
    inertia_moment: float = 38.8
    radius: float = 57.3
    s_wing: float = 5.34
    q: float = 1236.25
    b_a: float = 1.684
    n_x: float = -7.0
    m_part: float = 1.3
    m_all: float = 50.0


CONST_PARAMS = ConstParams()
STEP = timedelta(milliseconds=1)


def calc_main_moment(rocket_moment: float, attack_angle: float, elevator_angle: float) -> float:
    return rocket_moment + \
        (attack_angle * CONST_PARAMS.m_alpha_z *
         CONST_PARAMS.s_wing * CONST_PARAMS.q * CONST_PARAMS.b_a) / CONST_PARAMS.gravity + \
        (elevator_angle * CONST_PARAMS.m_delta_z *
         CONST_PARAMS.s_wing * CONST_PARAMS.q * CONST_PARAMS.b_a) / CONST_PARAMS.gravity


def calc_elevator_angle(attack_angle: float) -> float:
    return - CONST_PARAMS.m_alpha_z * attack_angle / CONST_PARAMS.m_delta_z


def calc_attack_angle(early_angle: float, angular_velocity: float) -> float:
    return early_angle + angular_velocity * STEP.total_seconds()


def calc_inertia_moment(j_la: float, j_t: float) -> float:
    return j_t + j_la


def calc_angular_acceleration(early_main_moment: float, early_inertia_moment) -> float:
    return early_main_moment * CONST_PARAMS.radius * CONST_PARAMS.gravity / early_inertia_moment


def calc_angular_velocity(early_angular_velocity: float, angular_velocity: float) -> float:
    return early_angular_velocity + angular_velocity * STEP.total_seconds()


def update_data(data: dict, cur_time: float) -> None:
    data["time [сек]"].append(cur_time)
    data["Iт"].append(CONST_PARAMS.inertia_moment)
    data["epsilon"].append(calc_angular_acceleration(data["Mz"][-1], data["Iт"][-1]))
    data["omega"].append(calc_angular_velocity(data["omega"][-1], data["epsilon"][-1]))
    data["alpha"].append(calc_attack_angle(data["alpha"][-1], data["omega"][-1]))
    data["delta_р.в."].append(calc_elevator_angle(data["alpha"][-2]))
    data["Mz"].append(calc_main_moment(data["Mzp"][-1], data["alpha"][-2], data["delta_р.в."][-1]))
    data["V"].append(0)
    data["Lp"].append(0)
    data["Mzp"].append(0)


def save(legend, data):
    with open("results.csv", 'w', encoding='utf-8') as file:

        file.write(';'.join(legend) + '\n')

        for string in data:
            file.write(";".join(map(str, string)) + '\n')


def plot(data: dict):
    abscissa = data["time [сек]"]
    colour = ["red", "blue", "green", "black", "purple"]
    params = ["epsilon", "omega", "alpha", "delta_р.в."]

    fig, axs = plt.subplots(len(params))

    for key, item in zip(params, range(len(params))):
        axs[item].plot(abscissa, data[key], colour[item])
        axs[item].set_title(key)

    plt.savefig("fig.jpg")
    plt.show()


@dataclass(repr=True)
class Rocket:
    time_start: timedelta
    flight_duration: timedelta
    weight: float = 15

    def consider_moment(self, calc_params: dict, current_time: float, index_started_rocket: int):

        if self.time_start == current_time:
            return 0
        else:
            velocity = self.velocity(calc_params["V"][-1])
            l_p = self.l_p(calc_params["Lp"][-1], velocity)
            calc_params["V"][-1] += velocity
            calc_params["Lp"][-1] += (self.l_p(l_p, velocity))

        return self.f_p() * l_p

    def f_p(self):
        return (self.weight + CONST_PARAMS.m_part) * CONST_PARAMS.gravity

    @staticmethod
    def l_p(early_value: float, velocity: float) -> float:
        return early_value + velocity * STEP.total_seconds()

    @staticmethod
    def velocity(early_velocity: float):
        return early_velocity + CONST_PARAMS.n_x * STEP.total_seconds()

    def inertia(self):
        pass


rockets = [
    Rocket(timedelta(seconds=4), timedelta(milliseconds=15), weight=15),
    Rocket(timedelta(seconds=8), timedelta(milliseconds=15), weight=15)
]


if __name__ == '__main__':

    flight_time = timedelta(seconds=10)
    current = timedelta(milliseconds=0)

    calc_data = {
        "time [сек]": [timedelta(0).total_seconds()],
        "Mz": [0.0],
        "epsilon": [0.0],
        "omega": [0.0],
        "alpha": [4.0],
        "Iт": [38.8],
        "delta_р.в.": [calc_elevator_angle(4.0)],
        "Mzp": [0.0],
        "V": [0.0],
        "Lp": [0.0]
    }

    while current < flight_time:

        update_data(calc_data, current.total_seconds())

        for rocket in rockets:
            if rocket.time_start < current <= rocket.time_start + rocket.flight_duration:
                calc_data["Mzp"][-1] += rocket.consider_moment(calc_data, current, rockets.index(rocket))

        current = current + STEP

    converted_data = [[calc_data[key][i] for key in calc_data.keys()] for i in range(len(calc_data['Mz']))]

    converted_data.pop(0)
    save(calc_data.keys(), converted_data)

    plot(calc_data)
