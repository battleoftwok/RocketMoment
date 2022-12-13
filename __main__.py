from dataclasses import dataclass, field
from datetime import timedelta
import matplotlib.pyplot as plt


SEPARATOR = ";"


@dataclass
class ConstParams:

    """
    Константы, используемые в расчёте
    """

    gravity: float = 9.81
    m_alpha_z: float = -.0033
    m_delta_z: float = -.0025
    radius: float = 57.3
    wing_area: float = 5.34
    q: float = 1236.25
    b_a: float = 1.684
    n_x: float = -7.0
    var_part_weight: float = 1.3
    airplane_wight: float = 132.55
    airplane_inertia_radius: float = field(default=0, init=False)
    pipe_inertia_radius: float = field(default=0, init=False)


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

    plt.savefig(f"fig.jpg")
    plt.show()


@dataclass
class Data:
    airplane_radius_moment_inertia: float = 0
    airplane_moment_inertia: float = 0
    rocket_radius_moment_inertia: float = 0
    rocket_moment_inertia: float = 0
    general_moment_inertia: float = 0
    airplane_acceleration: float = 0
    airplane_velocity: float = 0
    airplane_attack_angle: float = 0
    elevator_angle: float = 0
    rocket_velocity: float = 0
    rocket_way: float = 0
    rocket_power: float = 0
    rocket_moment: float = 0
    general_moment: float = 0

    def recalc_data(self):
        pass


@dataclass(repr=True)
class Rocket:
    coord_x: list
    coord_y: float
    time_start: timedelta
    flight_duration: timedelta
    weight: float = 15
    velocity = 0
    lp = 0


if __name__ == '__main__':

    rockets = [
        Rocket(coord_x=[0.055, 0.138, 0.221, 0.304, 0.387, 0.47,
                        0.553, 0.636, 0.719, 0.802, 0.885, 0.968,
                        1.051, 1.134, 1.217, 1.3],
               coord_y=.152,
               time_start=timedelta(seconds=4),
               flight_duration=timedelta(milliseconds=15)),

        Rocket(coord_x=[0.075, 0.148, 0.221, 0.294, 0.367, 0.44,
                        0.513, 0.586, 0.659, 0.732, 0.805, 0.878,
                        0.951, 1.024, 1.097, 1.17],
               coord_y=.099,
               time_start=timedelta(seconds=8),
               flight_duration=timedelta(milliseconds=15))
    ]

    flight_time = timedelta(seconds=10)
    current = timedelta(milliseconds=0)

    calc_data = Data()

    with open("result.csv", "w", encoding="utf-8") as file:

        print(SEPARATOR.join(map(str, calc_data.__dict__.keys())), file=file)

        while current <= flight_time:

            # calc_data.recalc_data(current)
            #
            # for rocket in rockets:
            #     if rocket.time_start <= current <= rocket.time_start + rocket.flight_duration:
            #         rocket.consider_moment(calc_data, current)

            flag = [rocket for rocket in rockets if
                    rocket.time_start <= current <= rocket.flight_duration + rocket.time_start]

            if bool(flag) is True:
                flag[0].consider_moment(calc_data, current)
            else:
                calc_data.recalc_data(current)

            print(SEPARATOR.join(map(str, calc_data.__dict__.values())), file=file)
            current = current + STEP
