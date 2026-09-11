def step(dynamics_fn, t, state, dt, params):
    h1 = dynamics_fn(t, state, params)
    h2 = dynamics_fn(t + dt/2, state + dt/2 *h1, params)
    h3 = dynamics_fn(t + dt/2, state + dt/2 *h2, params)
    h4 = dynamics_fn(t + dt, state + dt*h3, params)

    next_state = state + (dt/6) * (h1 + 2*h2 + 2*h3 + h4)
    return next_state