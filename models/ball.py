import numpy as np


def ball_dynamics(t, state, params):
    gravity = params["gravity"]

    height = state[0]
    velocity = state[1]

    acceleration = -gravity  # Simplified model for a falling ball

    state_derivative = np.array([velocity, acceleration])
    return state_derivative


def impact (state, params):
    """Check for impact with the ground and apply restitution if necessary."""
    restitution = params["restitution"]
    height = state[0]
    velocity = state[1]

    if height <= 0 and velocity < 0:
        # If ball has hit the ground, apply restitution
        new_velocity = -restitution * velocity
        # Reset height to ground level
        new_height = 0
        return np.array([new_height, new_velocity])
    else:
        # No impact, return original state
        return state  


def calculate_energy(state, params):
    """Compute energies for a state ``(2,)`` or trajectory ``(2, N)``."""
    gravity = params["gravity"]
    mass = params["mass"]

    height = state[0]  # indexes entire row "vectorized" if state is (2, N)
    velocity = state[1]

    kinetic_energy = 0.5 * mass * velocity ** 2
    potential_energy = mass * gravity * height
    return kinetic_energy, potential_energy