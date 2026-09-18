import numpy as np


def dynamics(t, state, params):
    gravity = params["gravity"]
    mass = params["mass"]
    restitution_coeff = params["restitution_coeff"]

    position = state[0]
    velocity = state[1]

    #this only applies to free fall, we will need to add a check for when the ball hits the ground and apply the restitution coefficient
    acceleration = -gravity

    state_derivative = np.array([velocity, acceleration])
    return state_derivative

def calculate_energy(state, params):
    """Compute energies for a state ``(2,)`` or trajectory ``(2, N)``."""
    gravity = params["gravity"]
    mass = params["mass"]

    position = state[0]  # indexes entire row "vectorized" if state is (2, N)
    velocity = state[1]

    kinetic_energy = 0.5 * mass * velocity ** 2
    potential_energy = mass * gravity * position
    return kinetic_energy, potential_energy