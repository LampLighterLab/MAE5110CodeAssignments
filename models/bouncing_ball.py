import numpy as np


def dynamics(t, state, params):
    gravity = params["gravity"] # m/s^2
    mass = params["mass"] # kg
    k_gnd = params["spring_constant_ground"] # N/m, positive for pushing up when the ball submerged
    c_gnd = params["damping_coefficient_ground"] # N/(m/s), possitive for dissipation
    h0 = params["ground_height"] # m

    height = state[0]
    velocity = state[1]

    # if above ground, only gravity acts
    force = - mass * gravity # N
    # otherwise the spring and damping forces act as well
    if (height <= h0).all():
        force += k_gnd * (h0 - height) - c_gnd * velocity

    dhdt = velocity
    dvdt = force / (mass + 1e-200) # avoid divide by zero
    return np.array([dhdt, dvdt])

def generate_params():
    params = {
        "gravity": 9.81,  # gravity m/s^2)
        "mass": 1.0,      # point mass at end of rod (kg)
        "spring_constant_ground": 100.0,    # N/m, positive for pushing up when the ball submerged
        "damping_coefficient_ground": 0.0,  # N/(m/s), possitive for dissipation
        "ground_height": 0.0,  # m
    }
    return params


def calculate_energy(state, params):
    """Compute energies for a state ``(2,)`` or trajectory ``(2, N)``."""
    gravity = params["gravity"] # m/s^2
    mass = params["mass"] # kg
    k_gnd = params["spring_constant_ground"] # N/m, positive for pushing up when the ball submerged
    c_gnd = params["damping_coefficient_ground"] # N/(m/s), possitive for dissipation
    h0 = params["ground_height"] # m

    height = state[0]  # indexes entire row "vectorized" if state is (2, N)
    velocity = state[1]

    kinetic_energy = 0.5 * mass * (velocity) ** 2
    potential_energy = mass * gravity * height

    # if below ground, add spring potential energy
    spring_potential_energy = 0.5 * k_gnd * (h0 - height) ** 2
    spring_potential_energy[height > h0] = 0.0 # zero out spring potential energy if above ground
    potential_energy += spring_potential_energy

    return potential_energy, kinetic_energy
