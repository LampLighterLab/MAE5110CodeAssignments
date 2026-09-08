import enum

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from integrators import rk4 as integrator
from models import rimless_wheel as model


def main():
    params = model.generate_params()

    timestep = 1e-3
    sim_time = 5.0

    theta_min, theta_max = np.deg2rad(-10.0), np.deg2rad(50.0)
    num_theta = 40
    theta_dot_min, theta_dot_max = np.deg2rad(-50.0), np.deg2rad(50.0)
    num_theta_dot = 40

    attractor_points = {attractor: [] for attractor in Attractor}

    alpha, gamma = params["alpha"], params["gamma"]

    # initial_state = np.array([gamma - alpha + 0.1, -1.0, 0.0])
    # time_traj, state_traj = simulate(initial_state, params, timestep, sim_time)
    # attractor = classify_attractor(state_traj)
    # print(attractor)
    # return

    for theta in tqdm(np.linspace(theta_min, theta_max, num_theta)):
        for theta_dot in tqdm(
            np.linspace(theta_dot_min, theta_dot_max, num_theta_dot), leave=False
        ):
            initial_state = np.array([theta, theta_dot, 0.0])

            if theta < (gamma - alpha) or (alpha + gamma) < theta:
                continue

            time_traj, state_traj = simulate(initial_state, params, timestep, sim_time)
            attractor = classify_attractor(state_traj)
            attractor_points[attractor].append((theta, theta_dot))

    colors = {
        Attractor.ROLLING: "#e63946",
        Attractor.STABLE: "#2a9d8f",
        Attractor.UNKNOWN: "#8338ec",
    }

    fig, ax = plt.subplots()
    num_points = sum(len(points) for points in attractor_points.values())
    marker_size = np.clip(5000 / max(num_points, 1), 10, 200)
    for attractor, points in attractor_points.items():
        if points:
            points = np.asarray(points)
            ax.scatter(
                np.rad2deg(points[:, 0]),
                np.rad2deg(points[:, 1]),
                color=colors[attractor],
                label=attractor.name.title(),
                s=marker_size,
            )

    ax.set_title("Rimless Wheel Attractors")
    ax.set_xlabel(r"Initial angle $\theta$ (deg)")
    ax.set_ylabel(r"Initial angular velocity $\dot{\theta}$ (deg/s)")
    ax.grid(alpha=0.25)
    ax.legend(title="Attractor")
    fig.tight_layout()
    plt.show()


def simulate(initial_state, params, timestep, sim_time):
    theta = initial_state[0]
    alpha, gamma = params["alpha"], params["gamma"]
    assert (gamma - alpha) < theta < (alpha + gamma)

    n_timesteps = int(sim_time / timestep) + 1
    time_traj = np.arange(n_timesteps) * timestep
    state_traj = np.zeros((3, n_timesteps))
    state_traj[:, 0] = initial_state

    # simulation loop
    for step in range(n_timesteps - 1):
        state_traj[:, step + 1] = model.discrete_dynamics(
            state_traj[:, step], integrator, timestep, params
        )

    return time_traj, state_traj


class Attractor(enum.Enum):
    ROLLING = 0
    STABLE = 1
    UNKNOWN = 2


def classify_attractor(state_traj) -> Attractor:
    STABLE_THRESH = 1e-4
    ROLLING_THRESH = 0.05

    angular_velocity = state_traj[1]

    if np.abs(angular_velocity[-1]) < STABLE_THRESH:
        return Attractor.STABLE
    else:
        pre_impact_steps = get_pre_impact_steps(state_traj)
        pointcare_velocities = angular_velocity[pre_impact_steps].flatten()
        diff = np.diff(pointcare_velocities)
        if np.abs(diff[-1]) < ROLLING_THRESH:
            return Attractor.ROLLING
        else:
            return Attractor.UNKNOWN


def get_pre_impact_steps(state_traj):
    global_height = state_traj[2]
    height_diff = np.diff(global_height)
    pre_impact_steps = np.argwhere(height_diff < 0)
    return pre_impact_steps


def plot_traj(time_traj, state_traj, params):
    angle = state_traj[0]
    angular_momentum = model.calculate_angular_momentum(state_traj, params)
    kinetic_energy, potential_energy = model.calculate_energy(state_traj, params)

    fig, (ax1, ax2, ax3) = plt.subplots(nrows=3)

    ax1.plot(time_traj, angle, label="Angle")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Angle (rad)")

    ax2.plot(time_traj, angular_momentum, label="Angular momentum")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Angular momentum")

    ax3.plot(time_traj, kinetic_energy, label="Kinetic energy")
    ax3.plot(time_traj, potential_energy, label="Potential energy ")
    ax3.plot(time_traj, kinetic_energy + potential_energy, label="Total energy")
    ax3.set_xlabel("Time (s)")
    ax3.set_ylabel("Energy")

    fig.legend()
    plt.show()


if __name__ == "__main__":
    main()
