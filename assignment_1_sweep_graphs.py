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


# some set-up

initial_state = np.array([0, -1])

common_timestep = 0.0001
sim_time = 10.0         

# time_traj, state_traj = hybrid.integrate(rimless_wheel,rk4.step, common_timestep, sim_time, initial_state, params)

#time_traj, state_traj = rimless_wheel_integrator.integrate(rimless_wheel.dynamics, common_timestep, sim_time, initial_state, params, rimless_wheel.detect_impact, rimless_wheel.apply_impact)

#ROA Calculations

LEFT, RIGHT = params["ramp_angle"] - params["alpha"], params["ramp_angle"] + params["alpha"]

theta_grid_steps = np.arange(LEFT, RIGHT, 0.25)
thetadot_grid_steps = np.arange(-10, 10, 1)

limit_cycle_converged = []
stopped_converged = []

for theta in theta_grid_steps:
    for thetadot in thetadot_grid_steps:
        initial_state = np.array([theta, thetadot])
        time_traj, state_traj = rimless_wheel_integrator.integrate(rimless_wheel.dynamics, common_timestep, sim_time, initial_state, params, rimless_wheel.detect_impact, rimless_wheel.apply_impact)
        

        if(state_traj[1,-1]  < -0.1):
            limit_cycle_converged.append(initial_state)
        else:
            stopped_converged.append(initial_state)


limit_cycle_converged = np.array(limit_cycle_converged)
stopped_converged     = np.array(stopped_converged)

print("Limit Cycle Converged Initial States: ", limit_cycle_converged)
print("Stopped Converged Initial States: ", stopped_converged)


# kinetic_energy, potential_energy = rimless_wheel.calculate_energy(state_traj, params)

# plt.figure()
# plt.plot(time_traj, potential_energy, label="Potential energy")
# plt.plot(time_traj, kinetic_energy, label="Kinetic energy")
# plt.plot(time_traj, potential_energy + kinetic_energy, label="Total energy")
# plt.xlabel("Time (s)")
# plt.ylabel("Energy (J)")
# plt.title("Pendulum energy")
# plt.legend()
# plt.tight_layout()
# plt.show()





#



# state space plot

# plt.figure()
# plt.plot(state_traj[0], state_traj[1], label="Phase Portrait")
# plt.xlabel("Angle(rad)")
# plt.ylabel("Angular Momentum(rad/sec)")
# plt.axvline(x=params["ramp_angle"] + params["alpha"], color='r', linestyle='--', label="Right Bound")
# plt.axvline(x=params["ramp_angle"] - params["alpha"], color='r', linestyle='--', label="Left Bound")
# plt.title("Rimless Wheel Phase Portrait")
# plt.legend()
# plt.tight_layout()
# plt.show()

#Plotting the limit cycle line - AI assisted
G, L = params["gravity"], params["length"]
a, g = params["alpha"], params["ramp_angle"]
LEFT, RIGHT = g - a, g + a

# The wheel rolls toward whichever guard has lower potential energy
# (PE = m*g*L*cos(theta)), lands there, and is reset to the other one.
if np.cos(LEFT) < np.cos(RIGHT):
    start, land, sign = RIGHT, LEFT, -1.0     # rolls toward -theta
else:
    start, land, sign = LEFT, RIGHT, +1.0     # rolls toward +theta

c = np.cos(2 * a)
D = (2 * G / L) * (np.cos(start) - np.cos(land))
omega_star = np.sqrt(c**2 * D / (1 - c**2))   # post-impact speed on the cycle

theta_cycle = np.linspace(start, land, 400)
thetadot_cycle = sign * np.sqrt(omega_star**2 + (2 * G / L) * (np.cos(start) - np.cos(theta_cycle)))


# plt.figure()
# plt.scatter(limit_cycle_converged[:, 0], limit_cycle_converged[:, 1], label="Limit Cycle Converged", color='green')
# if stopped_converged.size > 0:
#     plt.scatter(stopped_converged[:, 0], stopped_converged[:, 1], label="Stopped Converged", color='red')
# plt.xlabel("Angle(rad)")
# plt.ylabel("Angular Momentum(rad/sec)")
# plt.axvline(x=params["ramp_angle"] + params["alpha"], color='b', linestyle='--', label="Right Bound")
# plt.axvline(x=params["ramp_angle"] - params["alpha"], color='b', linestyle='--', label="Left Bound")
# plt.axhline(y=0, color='red', linestyle='--', label="Came to rest(Attractor)")
# plt.plot(theta_cycle, thetadot_cycle, 'k', lw=2, label="Limit cycle(Attractor)", color='green')
# plt.title("Rimless Wheel Phase Portrait")
# plt.grid()
# plt.legend()
# plt.tight_layout()
# plt.show()



