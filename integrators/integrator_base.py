from abc import ABC, abstractmethod
import numpy as np

class IntegratorBase(ABC):
    @abstractmethod
    def integrate(self, param_integrator, param_model, time_trajectory, initial_state, dynamics_function):
        """
        Integrate the system over time trajectory
        
        param_integrator:  dict, parameters for the integrator
        pram_model:        dict, parameters for the model
        time_trajectory:   [1xN] np array, time trajectory to integrate over
        initial_state:     [Mx1] np array, initial state of the system
        dynamics_function: (t: float, state: [Mx1] np.array, params: dict) -> [Mx1] np.array
        """
        print("IntegratorBase: integrate() method not implemented")
        N = len(time_trajectory)
        M = len(initial_state)
        state_trajectory = np.zeros((M, N))
        return state_trajectory
