import numpy as np


def dynamics_rimless_wheel(t, state, params):
    """Compute the time derivative of the state (i.e. state dynamics) for a rimless wheel."""
    gravity = params["gravity"]
    length = params["length"]

    angle = state[0]
    angular_velocity = state[1]

    acceleration = gravity/length * np.sin(angle)  # Simplified model for a rimless wheel

    state_derivative = np.array([angular_velocity, acceleration])
    return state_derivative


def impact(state, params):
    """Check for impact with new spoke, as well as apply new angular velocity
    and shift coordinates if necessary."""
    angle = state[0]
    angular_velocity = state[1]
    gamma = params["gamma"]
    number_of_spokes = params["number_of_spokes"]

    alpha = np.pi / number_of_spokes

    # Impact-event guard: next spoke has reached the ground.
    if angle >= (gamma + alpha) and angular_velocity > 0:
        # Conserve angular momentum about the new contact point
        new_angular_velocity = angular_velocity * np.cos(2*alpha)
        # Shift coordinate to the new stance spoke.
        new_angle = gamma - alpha
        return np.array([new_angle, new_angular_velocity]), True
    else:
        # No impact, return original state
        return state, False


def calculate_energy(state, params):
    """Compute energies for a state ``(2,)`` or trajectory ``(2, N)``."""
    gravity = params["gravity"]
    mass = params["mass"]
    length = params["length"]

    angle = state[0]  # indexes entire row "vectorized" if state is (2, N)
    angular_velocity = state[1]

    kinetic_energy = 0.5 * mass * (length ** 2) * (angular_velocity ** 2)
    potential_energy = mass * gravity * length * np.cos(angle)

    return kinetic_energy, potential_energy