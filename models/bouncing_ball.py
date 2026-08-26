import numpy as np

def dynamics(t, state, params):
    # Model a bouncing ball with a certain radius and coefficient of restitution
    # The ball cannot travel below y=0, the floor, and will bounce when it touches it
    # state needs to have four rows: x, xdot, y, ydot
    # This model assumes that there is no friction between the ground and ball (so it can't spin)

    # We have the issue that we don't know the timestep and can only set the derivatives of our state for one step
    # So we can't instantaneously change the position or velocity, since they only update by a tiny bit

    print("State starting dynamics calc:")
    print(state)
    gravity = params["gravity"]
    radius = params["radius"]
    mass = params["mass"]
    coeff_restitution = params["coeff_restitution"]

    x = state[0]  # horizontal position
    xdot = state[1]  # horizontal velocity
    y = state[2]  # vertical position
    ydot = state[3]  # vertical velocity

    ydotdot = -mass * gravity  # vertical acceleration
    print(f"t={t:.02f}, y={y}, ydot={ydot}")

    if y - radius < 0:
        # The edge of the ball collides with the ground! Bounce it!
        ydot = -ydot * coeff_restitution
        print(f"y below ground at t={t}; setting ydot={ydot}")
        # If we had direct control of position, we could also pop the ball above the ground

    state_deriv = np.array([xdot, 0, ydot, ydotdot])
    print(state_deriv)
    return state_deriv


def generate_params():
    # The params for the bouncing ball
    params = {
        "gravity": 9.81,  # gravity m/s^2)
        "radius": 0.1,  # ball radius (m)
        "mass": 0.5,  # mass of the ball (kg)
        "coeff_restitution": 1.0,  # coefficient of restitution (ratio of final velocity to initial velocity)
    }
    return params

def calculate_energy(state, params):
    gravity = params["gravity"]
    mass = params["mass"]

    xdot = state[1]  # horizontal velocity
    y = state[2]  # vertical position
    ydot = state[3]  # vertical velocity

    kinetic_energy = 0.5 * mass * ydot**2 + 0.5 * mass * xdot**2
    potential_energy = y * mass * gravity

    return kinetic_energy, potential_energy


# TODO: The ball doesn't bounce. Maybe model it as a spring that can compress to store energy before releasing it again?
