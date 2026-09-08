import matplotlib.pyplot as plt
import numpy as np

from integrators import rk4 as integrator
from models import rimless_wheel as model


def main():
    params = model.generate_params()

    # theta, theta dot, base height
    initial_state = np.array([np.deg2rad(10.0), np.deg2rad(0.0), 0.0])

    timestep = 1e-4
    sim_time = 5.0

    time_traj, state_traj = simulate(initial_state, params, timestep, sim_time)

    plot_traj(state_traj, time_traj, params)


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


def plot_traj(state_traj, time_traj, params):
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
