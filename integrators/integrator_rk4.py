from .integrator_base import IntegratorBase
import numpy as np

class IntegratorRK4(IntegratorBase):
    def integrate(self, param_integrator, param_model, time_trajectory, initial_state, dynamics_function):
        N = len(time_trajectory)
        M = len(initial_state)
        state_trajectory = np.zeros((M, N))
        state_trajectory[:, 0] = initial_state
        for step, t in enumerate(time_trajectory[:-1]):
            timestep = time_trajectory[step + 1] - time_trajectory[step] # "h" from wikipedia

            # The RK4 part
            k1 = dynamics_function(t, state_trajectory[:, step], param_model) # [Mx1]
            k2 = dynamics_function(t + timestep / 2, state_trajectory[:, step] + (timestep / 2) * k1, param_model) # [Mx1]
            k3 = dynamics_function(t + timestep / 2, state_trajectory[:, step] + (timestep / 2) * k2, param_model) # [Mx1]
            k4 = dynamics_function(t + timestep, state_trajectory[:, step] + timestep * k3, param_model) # [Mx1]

            state_trajectory[:, step + 1] = state_trajectory[:, step] + (timestep / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

            # for checking phase change: height of ball from positive to negative
            if (state_trajectory[0, step] * state_trajectory[0, step + 1]) < 0:
                print(f"Phase change at time {t}")
            
        return state_trajectory
