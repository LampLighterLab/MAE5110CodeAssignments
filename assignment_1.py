import argparse
import enum

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from integrators import rk4 as integrator
from models import rimless_wheel as model


def main():
    parser = argparse.ArgumentParser(description="Simulate the rimless wheel")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("attractors", help="plot the attractor map")
    subparsers.add_parser("trajectory", help="plot a single simulation")
    subparsers.add_parser("return", help="plot a single simulation")
    args = parser.parse_args()

    params = model.generate_params()

    timestep = 1e-3

    if args.command == "attractors":
        plot_attractors(params, timestep, sim_time=5.0)
    elif args.command == "trajectory":
        initial_state = np.array([np.deg2rad(10.0), np.deg2rad(0.0), 0.0])
        time_traj, state_traj = simulate(initial_state, params, timestep, sim_time=5.0)
        plot_traj(time_traj, state_traj, params)
    elif args.command == "return":
        plot_return_map(params, timestep, sim_time=5.0)


def plot_return_map(params, timestep, sim_time):
    THETA_DOT_MIN, THETA_DOT_MAX = np.deg2rad(-500.0), np.deg2rad(50.0)
    NUM_SAMPLES = 500  # sample many initial conditions
    FIXED_POINT_THRESHOLD = 0.01

    rng = np.random.default_rng(0)
    current_velocities = []
    next_velocities = []
    alpha, gamma = params["alpha"], params["gamma"]

    progress = tqdm(total=NUM_SAMPLES)
    sample_number = 0
    while sample_number < NUM_SAMPLES:
        theta = params["gamma"]
        theta_dot = rng.uniform(THETA_DOT_MIN, THETA_DOT_MAX)

        if theta <= (gamma - alpha) or (alpha + gamma) <= theta:
            continue

        initial_state = np.array([theta, theta_dot, 0.0])
        _, state_traj = simulate(initial_state, params, timestep, sim_time)
        pre_impact_steps = get_pre_impact_steps(state_traj)
        pre_impact_velocities = state_traj[1, pre_impact_steps].flatten()

        current_velocities.extend(pre_impact_velocities[:-1])
        next_velocities.extend(pre_impact_velocities[1:])
        sample_number += 1
        progress.update()

    progress.close()

    current_velocities = np.array(current_velocities)
    next_velocities = np.array(next_velocities)

    fixed_point_idx = np.argwhere(
        np.abs(next_velocities - current_velocities) < FIXED_POINT_THRESHOLD
    )
    fixed_points = current_velocities[fixed_point_idx]

    # We know there will be 2 fixed points, so we'll divide the set we found in two and average
    avg_fixed_point = np.mean(fixed_points)
    small_fixed_point = np.mean(fixed_points[fixed_points < avg_fixed_point])
    large_fixed_point = np.mean(fixed_points[fixed_points >= avg_fixed_point])

    fig, ax = plt.subplots()
    current_velocities_deg = np.rad2deg(current_velocities)
    next_velocities_deg = np.rad2deg(next_velocities)
    ax.scatter(
        current_velocities_deg,
        next_velocities_deg,
        color="#3a86ff",
        s=20,
        alpha=0.75,
    )

    velocity_min = min(min(current_velocities_deg), min(next_velocities_deg))
    velocity_max = max(max(current_velocities_deg), max(next_velocities_deg))

    velocity_padding = 0.05 * (velocity_max - velocity_min)
    plot_min = velocity_min - velocity_padding
    plot_max = velocity_max + velocity_padding

    ax.plot(
        [plot_min, plot_max],
        [plot_min, plot_max],
        "k--",
        label="Identity",
    )
    small_fixed_point_deg = np.rad2deg(small_fixed_point)
    large_fixed_point_deg = np.rad2deg(large_fixed_point)
    print(f"Small fixed-point estimate: {small_fixed_point_deg:.3f} deg/s")
    print(f"Large fixed-point estimate: {large_fixed_point_deg:.3f} deg/s")
    ax.scatter(
        small_fixed_point_deg,
        small_fixed_point_deg,
        color="#ff9f1c",
        edgecolor="black",
        marker="X",
        s=120,
        label="Small fixed point",
        zorder=3,
    )
    ax.scatter(
        large_fixed_point_deg,
        large_fixed_point_deg,
        color="#e71d36",
        edgecolor="black",
        marker="P",
        s=120,
        label="Large fixed point",
        zorder=3,
    )
    ax.set_xlim(plot_min, plot_max)
    ax.set_ylim(plot_min, plot_max)
    ax.set_title("Rimless Wheel Return Map")
    ax.set_xlabel(r"Pre-impact velocity $\dot{\theta}_k$ (deg/s)")
    ax.set_ylabel(r"Next pre-impact velocity $\dot{\theta}_{k+1}$ (deg/s)")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    plt.show()


def plot_attractors(params, timestep, sim_time):
    THETA_MIN, THETA_MAX = np.deg2rad(-10.0), np.deg2rad(50.0)
    NUM_THETA = 40
    THETA_DOT_MIN, THETA_DOT_MAX = np.deg2rad(-50.0), np.deg2rad(50.0)
    NUM_THETA_DOT = 40

    attractor_points = {attractor: [] for attractor in Attractor}

    alpha, gamma = params["alpha"], params["gamma"]

    for theta in tqdm(np.linspace(THETA_MIN, THETA_MAX, NUM_THETA)):
        for theta_dot in tqdm(
            np.linspace(THETA_DOT_MIN, THETA_DOT_MAX, NUM_THETA_DOT), leave=False
        ):
            initial_state = np.array([theta, theta_dot, 0.0])

            if theta < (gamma - alpha) or (alpha + gamma) < theta:
                continue

            _, state_traj = simulate(initial_state, params, timestep, sim_time)
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
    pre_impact_steps = np.argwhere(np.abs(height_diff) > 1e-6)
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
