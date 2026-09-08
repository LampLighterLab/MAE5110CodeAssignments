from .integrator_base import IntegratorBase
import numpy as np

class IntegratorRK4(IntegratorBase):
    def integrate(self, param_integrator, param_model, time_trajectory, initial_state, model, checkpoint_callback=None):
        N = len(time_trajectory)
        M = len(initial_state)
        state_trajectory = np.zeros((M, N))
        state_trajectory[:, 0] = initial_state
        for step, t in enumerate(time_trajectory[:-1]):
            timestep = time_trajectory[step + 1] - time_trajectory[step] # "h" from wikipedia

            # The RK4 part
            k1 = model.dynamics(t, state_trajectory[:, step], param_model) # [Mx1]
            k2 = model.dynamics(t + timestep / 2, state_trajectory[:, step] + (timestep / 2) * k1, param_model) # [Mx1]
            k3 = model.dynamics(t + timestep / 2, state_trajectory[:, step] + (timestep / 2) * k2, param_model) # [Mx1]
            k4 = model.dynamics(t + timestep, state_trajectory[:, step] + timestep * k3, param_model) # [Mx1]

            state_trajectory[:, step + 1] = state_trajectory[:, step] + (timestep / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

            # Call the checkpoint callback if it exists
            if checkpoint_callback:
                checkpoint_callback(t, state_trajectory[:, step], t + timestep, state_trajectory[:, step + 1], model)
            
        return state_trajectory
