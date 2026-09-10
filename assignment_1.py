import matplotlib.pyplot as plt
import numpy as np
from integrators import rk4 as integrator
from models import rimlesswheel as model

params = {
    "gravity": 9.81,
    "spoke_length": 1.0,
    "slope_angle": 0.1,
    "number_spokes": 8
}
def simulate(initial_state, params, timestep=0.005, sim_time=10, early_stopping=True):
    state = initial_state.copy()
    impact_velocities = []


    time = np.arange(0, sim_time, timestep)


    for t in time:
        state = integrator.step(
            model.dynamics,
            t,
            state,
            timestep,
            params
        )


        if model.detect_event(state, params):
            state = model.reset_state(state, params)
            impact_velocities.append(state[1])


            if early_stopping and check_convergence(impact_velocities):
                break


    return state, impact_velocities

def check_convergence(impact_velocities):
    if len(impact_velocities) < 5:
        return False

    recent_impacts = impact_velocities[-5:]

    return max(recent_impacts) - min(recent_impacts) < 0.01

def classify_initial_state(initial_state, params, timestep=0.005, early_stopping=True):
    _, impact_velocities = simulate(
        initial_state, params, timestep=timestep, early_stopping=early_stopping
    )
    return int(check_convergence(impact_velocities))

def calculate_roa(params, theta_count=40, velocity_count=50, timestep=0.001,
                  early_stopping=True):
    alpha = np.pi / params["number_spokes"]
    gamma = params["slope_angle"]

    theta_values = np.linspace(gamma - alpha, gamma + alpha, theta_count)
    theta_dot_values = np.linspace(0, 5, velocity_count)

    roa = np.zeros((len(theta_dot_values), len(theta_values)))

    for i, theta_dot in enumerate(theta_dot_values):
        for j, theta in enumerate(theta_values):

            initial_state = np.array([theta, theta_dot])

            roa[i, j] = classify_initial_state(
                initial_state,
                params,
                timestep=timestep,
                early_stopping=early_stopping
            )

    return theta_values, theta_dot_values, roa

def plot_roa(params):
    theta_values, theta_dot_values, roa = calculate_roa(params)

    plt.figure()

    plt.imshow(
        roa,
        origin="lower",
        aspect="auto",
        extent=[
            theta_values[0],
            theta_values[-1],
            theta_dot_values[0],
            theta_dot_values[-1]
        ]
    )

    plt.xlabel("Initial theta (rad)")
    plt.ylabel("Initial angular velocity (rad/s)")
    plt.title("Region of Attraction")
    plt.colorbar(label="Attractor")

    plt.show()

def one_step_map(theta_dot, params, timestep=0.001):
    alpha = np.pi / params["number_spokes"]
    gamma = params["slope_angle"]

    state = np.array([gamma - alpha, theta_dot])
    t = 0

    while t < 5:
        state = integrator.step(model.dynamics, t, state, timestep, params)
        t += timestep

        if model.detect_event(state, params):
            state = model.reset_state(state, params)
            return state[1]

    return np.nan


def plot_return_map(params):
    theta_dot_values = np.linspace(0.1, 3, 100)

    next_theta_dot_values = np.array([
        one_step_map(theta_dot, params)
        for theta_dot in theta_dot_values
    ])

    plt.figure()
    plt.plot(theta_dot_values, next_theta_dot_values, label="Return map")
    plt.plot(theta_dot_values, theta_dot_values, "--", label="Identity line")

    plt.xlabel("Current angular velocity")
    plt.ylabel("Next angular velocity")
    plt.legend()
    plt.show()

    fixed_point_index = np.nanargmin(
        np.abs(next_theta_dot_values - theta_dot_values)
    )

    print("Fixed point:", theta_dot_values[fixed_point_index])

    fixed_point = theta_dot_values[fixed_point_index]

    return fixed_point


def calculate_floquet(fixed_point, params, epsilon=0.001):

    velocity_below = fixed_point - epsilon
    velocity_above = fixed_point + epsilon

    next_below = one_step_map(velocity_below, params)
    next_above = one_step_map(velocity_above, params)

    floquet_multiplier = (
        next_above - next_below
    ) / (2 * epsilon)

    return floquet_multiplier

def find_fixed_point(params):
    theta_dot_values = np.linspace(0.1, 3, 100)

    next_theta_dot_values = np.array([
        one_step_map(theta_dot, params)
        for theta_dot in theta_dot_values
    ])

    difference = np.abs(next_theta_dot_values - theta_dot_values)

    fixed_point_index = np.nanargmin(difference)

    return theta_dot_values[fixed_point_index]

def sweep_slope(params):
    gamma_values = np.deg2rad(np.linspace(1, 10, 10))

    roa_sizes = []
    floquet_values = []

    for gamma in gamma_values:
        test_params = params.copy()
        test_params["slope_angle"] = gamma

        # RoA
        _, _, roa = calculate_roa(test_params, theta_count=15, velocity_count=20)
        roa_sizes.append(np.mean(roa == 1))

        # Floquet multiplier
        fixed_point = find_fixed_point(test_params)
        floquet = calculate_floquet(fixed_point, test_params)
        floquet_values.append(floquet)

    plt.figure()
    plt.plot(np.rad2deg(gamma_values), roa_sizes, "o-")
    plt.xlabel("Slope (degrees)")
    plt.ylabel("Fraction of state space attracted to rolling")
    plt.show()

    plt.figure()
    plt.plot(np.rad2deg(gamma_values), floquet_values, "o-")
    plt.xlabel("Slope (degrees)")
    plt.ylabel("Floquet multiplier")
    plt.show()


def sweep_spokes(params):
    spoke_values = range(6, 13)

    roa_sizes = []
    floquet_values = []

    for number_spokes in spoke_values:
        test_params = params.copy()
        test_params["number_spokes"] = number_spokes

        _, _, roa = calculate_roa(test_params, theta_count=15, velocity_count=20)
        roa_sizes.append(np.mean(roa == 1))

        fixed_point = find_fixed_point(test_params)
        floquet = calculate_floquet(fixed_point, test_params)
        floquet_values.append(floquet)

    plt.figure()
    plt.plot(spoke_values, roa_sizes, "o-")
    plt.xlabel("Number of spokes")
    plt.ylabel("Fraction of state space attracted to rolling")
    plt.show()

    plt.figure()
    plt.plot(spoke_values, floquet_values, "o-")
    plt.xlabel("Number of spokes")
    plt.ylabel("Floquet multiplier")
    plt.show()


if __name__ == "__main__":
    plot_roa(params)
    plot_return_map(params)
    
    fixed_point = plot_return_map(params)
    floquet = calculate_floquet(fixed_point, params)
    print("Floquet multiplier:", floquet)

    sweep_slope(params)
    sweep_spokes(params)