import numpy as np


def dynamics(t, state, params):
    gravity = params["gravity"]
    mass = params["mass"]
    damping = params["damping"]
    stiffness = params["stiffness"]
 
    height = state[0]
    velocity = state[1]
 
    if height < 0:
        contact_force = -stiffness * height - damping*velocity #spring-damper force coming up from the ground
    else:
        contact_force = 0.0
 
    height_dot = velocity
    velocity_dot = -gravity + contact_force / mass
 
    state_derivative = np.array([height_dot, velocity_dot])
    return state_derivative


def generate_params():
    params = {
        "gravity": 9.81,        # gravity (m/s^2)
        "mass": 0.2,            # ball mass (kg)
        "damping": 3,
        "stiffness": 5000

    }
    return params


def calculate_energy(state, params):
    gravity = params["gravity"]
    damping = params["damping"]
    mass = params["mass"]
    stiffness = params["stiffness"]
    position = state[0]  #from ground, ground is 0 reference
    velocity = state[1]

    kinetic_energy = 0.5 * mass * (velocity) ** 2
    potential_energy = mass * gravity * position
    return kinetic_energy, potential_energy
