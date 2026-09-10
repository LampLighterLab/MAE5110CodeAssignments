from turtle import color

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

from models import rimless_wheel as model
from integrators import explicit_euler, rk4


# Basic simulation of a rimless wheel

params = {
    "gravity": 9.81,  # gravity (m/s^2)
    "mass": 1.0,  # mass of ball (kg)
    "length": 1.0,  # spoke length (m)
    "number_of_spokes": 8,  # number of spokes
    "gamma": 0.08,  # downhill inclination of the ground (rad)
}

# some set-up
initial_state = np.array([0.2, 2])
alpha = np.pi / params["number_of_spokes"]

if initial_state[0] >= params["gamma"] + alpha:
    raise ValueError(
        f"Starting angle is too large. "
        f"Choose an angle less than {params["gamma"] + alpha:.3f} rad.")

timestep = 1e-2
sim_time = 5.0


def simulate_rimless_wheel(integrator, timestep, sim_time, initial_state, params):
    n_timesteps = int(sim_time / timestep) + 1
    time_traj = np.arange(n_timesteps) * timestep
    state_traj = np.zeros((2, n_timesteps))
    state_traj[:, 0] = initial_state

    post_impact_velocities = []
    impact_times = []

    # Simulation loop with explicit_euler or rk4
    for step, t in enumerate(time_traj[:-1]):
        state_traj[:, step + 1] = integrator(
            state_traj[:, step], timestep, model.dynamics_rimless_wheel, t, params)

        # Check for impact
        state_traj[:, step + 1], did_impact = model.impact(state_traj[:, step + 1], params)
        if did_impact:
            post_impact_velocities.append(state_traj[1, step + 1])
            impact_times.append(t + timestep)

    return state_traj, time_traj, np.array(post_impact_velocities), np.array(impact_times)

state_traj, time_traj, post_impact_velocities, impact_times = simulate_rimless_wheel(rk4, timestep, sim_time, initial_state, params)
kinetic_energy, potential_energy = model.calculate_energy(state_traj, params)

# Estimating region of attraction
gravity = params["gravity"]
length = params["length"]
gamma = params["gamma"]

angle_values = np.linspace(-0.2, gamma + alpha - 1e-3, 101)
angular_velocity_values = np.linspace(-0.5, 3.0, 101)

# Exact pre-impact steady state angular velocity from energy balance derivation
angular_velocity_minus_steady = np.sqrt(
    (2 * gravity * (np.cos(gamma - alpha) - np.cos(gamma + alpha))) / (length * (np.sin(2 * alpha) ** 2)))
# Post-impact steady state angular velocity
angular_velocity_plus_steady = angular_velocity_minus_steady * np.cos(2 * alpha)

Angle, Angular_velocity = np.meshgrid(angle_values, angular_velocity_values)

roa = np.full(Angle.shape, 2, dtype=int)
roa_timestep = 5e-3
roa_sim_time = 10.0
velocity_tolerance = 0.15
fixed_point_tolerance = 0.15
min_impacts = 5

for i in range(Angle.shape[0]):
    for j in range(Angle.shape[1]):
        init_state = np.array([Angle[i, j], Angular_velocity[i, j]])

        if init_state[0] >= gamma + alpha:
            continue

        try:
            roa_state_traj, roa_time_traj, impact_velocities, impact_times = (
                simulate_rimless_wheel(rk4, roa_timestep, roa_sim_time, init_state, params))

            # Classify attractor:
            # Attractor 0: Settles to rest
            # Attractor 1: Steady periodic rolling
            # Attractor 2: Unknown/other behaviors
            
            # Check for attractor 0
            recent_states = roa_state_traj[:, -int(1.0 / roa_timestep):]
            final_state = recent_states[:, -1]

            if (np.allclose(recent_states, final_state[:, np.newaxis],
                atol=fixed_point_tolerance, rtol=0) and np.isclose(final_state[1],
                0.0, atol=fixed_point_tolerance, rtol=0)):
                    roa[i, j] = 0
                    continue

            # Check for attractor 1 (steady periodic rolling)
            if len(impact_velocities) >= min_impacts:
                recent_impact_velocities = impact_velocities[-min_impacts:]
                if np.allclose(recent_impact_velocities, recent_impact_velocities[0], atol=velocity_tolerance):
                    roa[i, j] = 1
                    continue

            # If neither attractor 0 nor attractor 1 is detected, classify as attractor 2
            roa[i, j] = 2

        except (ValueError, FloatingPointError):
            roa[i, j] = 2

# Plot the energies
plt.figure()
plt.plot(time_traj, potential_energy, label="Potential energy")
plt.plot(time_traj, kinetic_energy, label="Kinetic energy")
plt.plot(time_traj, potential_energy + kinetic_energy, label="Total energy")
plt.xlabel("Time (s)")  
plt.ylabel("Energy (J)")
plt.title(f"Rimless Wheel Energy (dt = {timestep:.5f})")
plt.legend()
plt.tight_layout()
plt.show()

# Plot the phase portrait
plt.figure()
plt.plot(state_traj[0, :], state_traj[1, :])
plt.xlabel("Angle (rad)")
plt.ylabel("Angular Velocity (rad/s)")
plt.title(f"Rimless Wheel Phase Portrait (dt = {timestep:.5f})")
plt.axhline(0, color='k', linestyle='-', linewidth=1)
plt.tight_layout()
plt.show()

# Plot region of attraction
cmap = plt.get_cmap("viridis")
color1 = cmap(0.16)
color2 = cmap(0.50)
color3 = cmap(0.83)
plt.figure(figsize=(8, 6))
plt.contourf(Angle, Angular_velocity, roa, levels=[-0.5, 0.5, 1.5, 2.5], cmap="viridis")
plt.xlabel("Initial Angle (rad)")
plt.ylabel("Initial Angular Velocity (rad/s)")
plt.title("Regions of Attraction")
legend_elements = [Patch(label="Rest", color=color1), Patch(label="Steady State", color=color2), 
                   Patch(label="Unknown / Other", color=color3)]
plt.legend(handles=legend_elements)
plt.grid(True, linestyle=":", alpha=0.6)
plt.tight_layout()
plt.show()