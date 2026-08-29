import numpy as np
import matplotlib.pyplot as plt

from models import pendulum as model

# Basic simulation of the pendulum

params = {
    "gravity": 9.81,  # gravity m/s^2)
    "length": 1,  # rod length (m)
    "mass": 0.2,  # point mass at end of rod (kg)
    "damping_coeff": 0.0,  # damping coefficient (kg*m^2/s)
}

# parameters
# integrator_type = "euler"  # "euler" or "rk4"
integrator_type = "rk4"    # "euler" or "rk4"

initial_state = np.array([np.pi / 4, 0.0])

# euler: ok at 100, blow up at 1000
# timestep = 1e-5 * 1000
# rk4: ok at 10000, blow up at 100000
timestep = 1e-5 * 100000
sim_time = 5.0

n_timesteps = int(sim_time / timestep) + 1
time_traj = np.arange(n_timesteps) * timestep

# simulation loop
# Deprecated: explicit Euler integration
# state_traj = np.zeros((2, n_timesteps))
# state_traj[:, 0] = initial_state
# for step, t in enumerate(time_traj[:-1]):
#     state_traj[:, step + 1] = state_traj[:, step] + timestep * model.dynamics(
#         t, state_traj[:, step], params
#     )
# New abstractive signiture
integrator = None
if integrator_type == "euler":
    from integrators import integrator_euler as integrator_module
    integrator = integrator_module.IntegratorEuler()
elif integrator_type == "rk4":
    from integrators import integrator_rk4 as integrator_module
    integrator = integrator_module.IntegratorRK4()
else:
    raise ValueError(f"Unknown integrator type: {integrator_type}")
state_traj = integrator.integrate(
    param_integrator={},
    param_model=params,
    time_trajectory=time_traj,
    initial_state=initial_state,
    dynamics_function=model.dynamics
)

# sanity check the energies: since there is no actuation, and no damping, total energy should stay
# constant. If we turn on the damping coefficient, it should slowly bleed out energy until it comes to
# a stand-still.

potential_energy, kinetic_energy = model.calculate_energy(state_traj, params)

plt.figure()
plt.plot(time_traj, potential_energy, label="Potential energy")
plt.plot(time_traj, kinetic_energy, label="Kinetic energy")
plt.plot(time_traj, potential_energy + kinetic_energy, label="Total energy")
plt.xlabel("Time (s)")
plt.ylabel("Energy (J)")
plt.title("Pendulum energy")
plt.legend()
plt.tight_layout()
plt.show()

# TODO: make a phase portrait plot
