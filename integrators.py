import numpy as np

def explicit_euler(t, state, timestep, dynamics_func, params):
    """Explicit Euler integration step."""
    state_derivative = dynamics_func(t, state, params)
    next_state = state + timestep * state_derivative
    return next_state

def rk4(t, state, timestep, dynamics_func, params):
    """Runge-Kutta 4th order integration step."""
    k1 = dynamics_func(t, state, params)
    k2 = dynamics_func(t + timestep / 2, state + (timestep / 2) * k1, params)
    k3 = dynamics_func(t + timestep / 2, state + (timestep / 2) * k2, params)
    k4 = dynamics_func(t + timestep, state + timestep * k3, params)

    next_state = state + (timestep / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
    return next_state