import numpy as np
from scipy.integrate import solve_ivp


def simulate(state0, params, sim_time, model, max_step=0.05, max_impacts=1000):
    """Simulate a hybrid system (continuous dynamics + instantaneous reset)
    from state0 for sim_time seconds, stitching together stance phases at
    each impact event.

    `model` must expose:
        model.dynamics(t, state, params)      -> state_derivative
        model.detect_impact(t, state, params) -> guard value (w/ .terminal,
                                                  .direction already set)
        model.reset_state(state, params)      -> post-impact state

    Returns a dict with the full stitched trajectory plus a record of every
    impact (time, pre-impact state, post-impact state) -- the impact record
    is what you'll want for classifying attractors and building return maps.
    """
    t0 = 0.0
    state = np.array(state0, dtype=float)

    time_all = [t0]
    state_all = [state.copy()]

    impact_times = []
    impact_states_pre = []
    impact_states_post = []

    guard = lambda t, y: model.detect_impact(t, y, params)
    guard.terminal = model.detect_impact.terminal
    guard.direction = model.detect_impact.direction

    n_impacts = 0
    while t0 < sim_time and n_impacts < max_impacts:
        sol = solve_ivp(
            lambda t, y: model.dynamics(t, y, params),
            (t0, sim_time),
            state,
            events=guard,
            max_step=max_step,
        )

        # append everything after the initial point (already recorded)
        time_all.extend(sol.t[1:])
        state_all.extend(sol.y[:, 1:].T)

        if sol.t_events[0].size > 0:
            impact_time = sol.t_events[0][0]
            pre_state = sol.y_events[0][0]
            post_state = model.reset_state(pre_state, params)

            impact_times.append(impact_time)
            impact_states_pre.append(pre_state)
            impact_states_post.append(post_state)

            # record the jump as a second point at the same time, so plots
            # show the discontinuity instead of interpolating through it
            time_all.append(impact_time)
            state_all.append(post_state)

            t0 = impact_time
            state = post_state
            n_impacts += 1
        else:
            # reached sim_time with no further impact
            break

    return {
        "time": np.array(time_all),
        "state": np.array(state_all).T,  # shape (2, N)
        "impact_times": np.array(impact_times),
        "impact_states_pre": np.array(impact_states_pre),   # shape (n_impacts, 2)
        "impact_states_post": np.array(impact_states_post), # shape (n_impacts, 2)
    }