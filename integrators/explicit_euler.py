import numpy as np

#never called this method
def time_trajectory(n_timesteps, timestep):
    initial_state = np.array([np.pi / 4, 0.0])

    #timestep = 1e-5
    #sim_time = 5.0

    #n_timesteps = int(sim_time / timestep) + 1
    time_traj = np.arange(n_timesteps) * timestep
    return time_traj


#never called this method
def state_trajectory(n_timesteps):
    initial_state = np.array([np.pi / 4, 0.0])

    #timestep = 1e-5
    #sim_time = 5.0

    #n_timesteps = int(sim_time / timestep) + 1
    #time_traj = np.arange(n_timesteps) * timestep
    state_traj = np.zeros((2, n_timesteps))
    state_traj[:, 0] = initial_state
    return state_traj

def step(function, t, state, dt, params):
    state_derivative = function(t, state, params) #this is the "last step, advanced by dt"
    next_state = state + dt * state_derivative
    return next_state