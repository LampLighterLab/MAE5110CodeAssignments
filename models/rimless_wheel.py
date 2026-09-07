import numpy as np
import numpy.typing as npt

from integrators import Integrator


def discrete_dynamics(
    state: npt.NDArray,
    integrator: Integrator,
    dt: float,
    params,
) -> npt.NDArray:
    alpha = params["alpha"]
    gamma = params["gamma"]

    _, theta_dot = state
    new_state = integrator(lambda _, x: swing_dynamics(x, params), 0.0, state, dt)
    theta_new, theta_dot_new = new_state

    if theta_new > alpha + gamma:
        theta_new = gamma - alpha
        theta_dot_new = theta_dot * np.cos(2 * alpha)

    # TODO: work out how to do the opposite direction

    return np.array([theta_new, theta_dot_new])


def swing_dynamics(state: npt.NDArray, params):
    gravity = params["gravity"]
    length = params["length"]

    theta, theta_dot = state
    theta_double_dot = gravity * np.sin(theta) / length

    return np.array([theta_dot, theta_double_dot])


def generate_params():
    params = {
        "gravity": 9.81,  # gravity m/s^2)
        "length": 1,  # rod length (m)
        "mass": 1,  # point mass at end of rod (kg)
        "alpha": np.deg2rad(360.0 / 6) / 2.0,
        "gamma": np.deg2rad(80),
    }
    return params


def calculate_angular_momentum(states: npt.NDArray, params):
    mass = params["mass"]
    length = params["length"]
    return mass * length**2 * states[1]


def calculate_energy(states: npt.NDArray, params):
    mass = params["mass"]
    length = params["length"]

    # inertia = mass * length ** 2
    # kinetic_energy = 1/2 * mass *
