import numpy as np
import matplotlib.pyplot as plt
import timeit

from models import ball as model
from integrators import explicit_euler, rk4


# Basic simulation of a bouncing ball

params = {
    "gravity": 9.81,  # gravity (m/s^2)
    "mass": 0.2,  # mass of ball (kg)
    "restitution": 0.5,  # coefficient of restitution (dimensionless); 0 = perfectly inelastic, 1 = perfectly elastic
}

# some set-up
initial_state = np.array([1.0, 0.0])

# Sweep and find the largest timestep where the integration stays stable
timesteps = np.arange(1e-5, 1e-0, 1e-5)
euler_stable_timesteps = []
rk4_stable_timesteps = []
sim_time = 3.0

def ball_simulation(integrator, timestep, sim_time, initial_state, params):
    n_timesteps = int(sim_time / timestep) + 1
    time_traj = np.arange(n_timesteps) * timestep
    state_traj = np.zeros((2, n_timesteps))
    state_traj[:, 0] = initial_state

    # Simulation loop with explicit_euler or rk4
    for step, t in enumerate(time_traj[:-1]):
        state_traj[:, step + 1] = integrator(
            state_traj[:, step], timestep, model.ball_dynamics, t, params)

        # Check for impact with the ground and apply restitution if necessary
        state_traj[:, step + 1] = model.impact(state_traj[:, step + 1], params)

    # sanity check the energies: since there is no actuation, and no damping, total energy should stay
    # constant. If we turn on the damping coefficient, it should slowly bleed out energy until it comes to
    # a stand-still.
    kinetic_energy, potential_energy = model.calculate_energy(state_traj, params)
    # Initially was potential_energy, kinetic_energy = model.calculate_energy(state_traj, params)

    # For finding the largest timestep that stays numerically accurate, we will find the relative error between 
    # the total energy calculated at the beginning of the simulation and the total energy calculated each timestep.  
    # If the relative error exceeds 1e-3, we will consider the timestep to be too large and not numerically stable.

    if params["restitution"] == 1.0:
        total_energy = potential_energy + kinetic_energy
        initial_total_energy = total_energy[0]
        relative_error = np.abs((total_energy - initial_total_energy) / initial_total_energy)
        if np.max(relative_error) < 1e-3:
            stable = True
        else:
            stable = False

    # If restitution is less than 1.0, we will consider all timesteps to be unstable.
    # Since energy will naturally decay over time, it becomes harder to varify stability.
    if params["restitution"] != 1.0:
        stable = False
    
    return state_traj, time_traj, stable

for timestep in timesteps:
    state_traj, time_traj, stable = ball_simulation(explicit_euler, timestep, sim_time, initial_state, params)
    if stable:
        euler_stable_timesteps.append(timestep)
    state_traj, time_traj, stable = ball_simulation(rk4, timestep, sim_time, initial_state, params)
    if stable:
        rk4_stable_timesteps.append(timestep)

# Find largest stable timestep (Explicit Euler and Runge-Kutta)
if len(euler_stable_timesteps) > 0:
    euler_largest_stable_timestep = max(euler_stable_timesteps)
else:
    euler_largest_stable_timestep = 1e-5

if len(rk4_stable_timesteps) > 0:
    rk4_largest_stable_timestep = max(rk4_stable_timesteps)
else:
    rk4_largest_stable_timestep = 1e-5

print(f"Largest Stable Timestep (Explicit Euler): {euler_largest_stable_timestep}")
print(f"Largest Stable Timestep (Runge-Kutta): {rk4_largest_stable_timestep}")

euler_state_traj, euler_time_traj, _ = ball_simulation(explicit_euler, euler_largest_stable_timestep, sim_time, initial_state, params)
rk4_state_traj, rk4_time_traj, _ = ball_simulation(rk4, rk4_largest_stable_timestep, sim_time, initial_state, params)

euler_kinetic_energy, euler_potential_energy = model.calculate_energy(euler_state_traj, params)
rk4_kinetic_energy, rk4_potential_energy = model.calculate_energy(rk4_state_traj, params)

# Using timeit to compare how fast the code is with each integrator
# Same-sized timestep (1e-5)
t_euler_same = timeit.timeit(lambda: ball_simulation(explicit_euler, 1e-5, sim_time, initial_state, params), number=10)
t_rk4_same = timeit.timeit(lambda: ball_simulation(rk4, 1e-5, sim_time, initial_state, params), number=10)

# Largest timestep that stayed numerically accurate for each integrator
t_euler_max = timeit.timeit(lambda: ball_simulation(explicit_euler, euler_largest_stable_timestep, sim_time, initial_state, params), number=10)
t_rk4_max = timeit.timeit(lambda: ball_simulation(rk4, rk4_largest_stable_timestep, sim_time, initial_state, params), number=10)

print("Same-Sized Timestep")
print(f"Explicit Euler: dt=1e-5: {t_euler_same:.3f} s")
print(f"Runge-Kutta: dt=1e-5: {t_rk4_same:.3f} s")

print(f"Largest Timestep")
print(f"Explicit Euler: dt={euler_largest_stable_timestep:.5f}: {t_euler_max:.3f} s")
print(f"Runge-Kutta: dt={rk4_largest_stable_timestep:.5f}: {t_rk4_max:.3f} s")

# Plotting the energies and phase portrait for the largest stable timestep for Explicit Euler
plt.figure()
plt.plot(euler_time_traj, euler_potential_energy, label="Potential energy")
plt.plot(euler_time_traj, euler_kinetic_energy, label="Kinetic energy")
plt.plot(euler_time_traj, euler_potential_energy + euler_kinetic_energy, label="Total energy")
plt.xlabel("Time (s)")
plt.ylabel("Energy (J)")
plt.title(f"Explict Euler Ball Energy (dt = {euler_largest_stable_timestep:.5f})")
plt.legend()
plt.tight_layout()
plt.show()

# Phase portrait: plotting angular velocity vs angle
plt.figure()
plt.plot(euler_state_traj[0, :], euler_state_traj[1, :])
plt.xlabel("Angle (rad)")
plt.ylabel("Angular Velocity (rad/s)")
plt.title(f"Explict Euler Ball Phase Portrait (dt = {euler_largest_stable_timestep:.5f})")
plt.axhline(0, color='k', linestyle='-', linewidth=1)  # Vertical line at x=0 to better see any deviations
plt.tight_layout()
plt.show()

# Plotting the energies and phase portrait for the largest stable timestep for Runge-Kutta
plt.figure()
plt.plot(rk4_time_traj, rk4_potential_energy, label="Potential energy")
plt.plot(rk4_time_traj, rk4_kinetic_energy, label="Kinetic energy")
plt.plot(rk4_time_traj, rk4_potential_energy + rk4_kinetic_energy, label="Total energy")
plt.xlabel("Time (s)")
plt.ylabel("Energy (J)")
plt.title(f"Runge-Kutta Ball Energy (dt = {rk4_largest_stable_timestep:.5f})")
plt.legend()
plt.tight_layout()
plt.show()

# Phase portrait: plotting angular velocity vs angle
plt.figure()
plt.plot(rk4_state_traj[0, :], rk4_state_traj[1, :])
plt.xlabel("Height (m)")
plt.ylabel("Velocity (m/s)")
plt.title(f"Runge-Kutta Ball Phase Portrait (dt = {rk4_largest_stable_timestep:.5f})")
plt.axhline(0, color='k', linestyle='-', linewidth=1)  # Vertical line at x=0 to better see any deviations
plt.tight_layout()
plt.show()