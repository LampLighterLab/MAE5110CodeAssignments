import numpy as np
import matplotlib.pyplot as plt
import timeit

from models import rimless_wheel
from integrators import rimless_wheel_integrator


# Basic simulation of the rimless_wheel

params = {
    "gravity": 9.81,  # gravity m/s^2)
    "length": 0.5,  # rod length (m)
    "mass": 0.2,  # point mass at end of rod (kg)
    "ramp_angle": -np.pi / 9,  # ramp angle (rad)
    "number_of_spokes": 6,
    "alpha": np.pi / 6   # spoke angle (rad)
}


# Set Up

initial_state = np.array([-0.1, 0])
common_timestep = 0.0001
sim_time = 5.0

# time_traj, state_traj = rimless_wheel_integrator.integrate(rimless_wheel.dynamics, common_timestep, sim_time, initial_state, params, rimless_wheel.detect_impact, rimless_wheel.apply_impact)


# plt.figure()
# plt.plot(state_traj[0, :], state_traj[1, :])
# plt.xlabel("Angle(rad)")
# plt.ylabel("Angular Momentum(rad/sec)")
# plt.title("Rimless Wheel Phase Portrait")
# plt.axvline(x=params["ramp_angle"] + params["alpha"], color='b', linestyle='--', label="Right Bound")
# plt.axvline(x=params["ramp_angle"] - params["alpha"], color='b', linestyle='--', label="Left Bound")
# plt.show()






n_timesteps = int(sim_time / common_timestep) + 1
time_traj = np.arange(n_timesteps) * common_timestep
state_traj = np.zeros((2, n_timesteps))
state_traj[:, 0] = initial_state

angular_velocity_at_impact = []

impact_numbers = []
impact_number = 0  # initial impact number is 0

# simulation loop
for step, t in enumerate(time_traj[:-1]):

    state_traj[:, step + 1] = state_traj[:, step] + common_timestep * rimless_wheel.dynamics(t, state_traj[:, step], params)

    #overwrite the state + 1 if an impact is detected
    if(rimless_wheel.detect_impact(state_traj[:, step + 1], params)):
        impact_number += 1
        impact_numbers.append(impact_number)
        state_traj[:, step + 1] = rimless_wheel.apply_impact(state_traj[:,step + 1],params)
        angular_velocity_at_impact.append(state_traj[1, step + 1])

    # print("impact", state_traj[:,step + 1])

# Getting Return Map - AI assisted
LEFT, RIGHT = params["ramp_angle"] - params["alpha"], params["ramp_angle"] + params["alpha"]

# The wheel rolls toward whichever guard has lower potential energy
# (PE = m*g*L*cos(theta)), lands there, and is reset to the other one.
if np.cos(LEFT) < np.cos(RIGHT):
    start, land, sign = RIGHT, LEFT, -1.0     # rolls toward -theta
else:
    start, land, sign = LEFT, RIGHT, +1.0     # rolls toward +theta

angulat_velocity_at_impact_multiplier = np.cos(2 * params["alpha"])
energy_gained_over_step = (2 * params["gravity"] / params["length"]) * (np.cos(start) - np.cos(land))
omega_star = np.sqrt(angulat_velocity_at_impact_multiplier**2 * energy_gained_over_step / (1 - angulat_velocity_at_impact_multiplier**2))   # post-impact speed on the cycle



# ---- step-to-step return map ----
w = np.linspace(0.1, 3.5, 300)

plt.figure()
plt.plot(w, angulat_velocity_at_impact_multiplier * np.sqrt(w**2 + energy_gained_over_step), lw=2, label=r"Return map $P(\omega)$")
plt.plot(w, w, '--', label=r"Identity $\omega_{n+1} = \omega_n$")
plt.plot(omega_star, omega_star, 'o', ms=9, label="Fixed point")
plt.xlabel(r"$\omega_n^+$ [rad/s]")
plt.ylabel(r"$\omega_{n+1}^+$ [rad/s]")
plt.title("Rimless Wheel Step-to-Step Return Map")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# plt.figure()
# plt.scatter(angular_velocity_at_impact[:-1], angular_velocity_at_impact[1:])
# plt.xlabel("$\omega_n$ (rad/s)")
# plt.ylabel("$\omega_{n+1}$ (rad/s)")
# plt.title("Rimless Wheel Poincaré section Analysis")
# plt.axhline(y = -omega_star, color='g', linestyle='--', label="Limit Cycle Angular Velocity")
# plt.legend()
# plt.show()










