import numpy as np
import matplotlib.pyplot as plt

from models import rimless_wheel as model
from integrators import rk4 as integrator

params = model.generate_params()
initial_state = np.array([np.deg2rad(10.0), 0.0])

timestep = 1e-4
sim_time = 5.0

n_timesteps = int(sim_time / timestep) + 1
time_traj = np.arange(n_timesteps) * timestep
state_traj = np.zeros((2, n_timesteps))
state_traj[:, 0] = initial_state

# simulation loop
for step, t in enumerate(time_traj[:-1]):
    state_traj[:, step + 1] = model.discrete_dynamics(
        state_traj[:, step], integrator, timestep, params
    )

angle = state_traj[0]
angular_momentum = model.calculate_angular_momentum(state_traj, params)

fig, ax1 = plt.subplots()

ax1.plot(time_traj, angle, label="Angle")
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("Angle (rad)")

ax2 = ax1.twinx()
ax2.plot(time_traj, angular_momentum, label="Angular momentum", color="red")
ax2.set_ylabel("Angular momentum")

fig.legend()
fig.tight_layout()
plt.show()
