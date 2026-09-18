import numpy as np
import matplotlib.pyplot as plt

from models import rimless_wheel as model
from simulate import simulate
from assignment_1b import compute_roa_grid, LABEL_TO_INT


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def get_limit_cycle_theta_dot_star(params, theta_dot0=2.5, sim_time=20.0, tail=5):
    """Run one long simulation from a healthy initial velocity (enough to
    clear the first hump) and return the converged post-impact theta_dot
    -- our estimate of the return map's fixed point."""
    alpha = np.pi / params["num_spokes"]
    theta0 = params["slope"] - alpha + 0.05

    result = simulate(
        state0=[theta0, theta_dot0],
        params=params,
        sim_time=sim_time,
        model=model,
        max_step=0.02,
    )
    post_theta_dots = result["impact_states_post"][:, 1]
    if len(post_theta_dots) == 0:
        raise RuntimeError("Never impacted -- raise theta_dot0 or check params.")
    return post_theta_dots, np.mean(post_theta_dots[-tail:])


def step_once(theta_dot_in, params, sim_time_cap=10.0):
    """Start exactly at the standard post-impact angle with the given
    theta_dot, and return the theta_dot after the NEXT impact (i.e. one
    application of the return map). Returns None if it never impacts."""
    alpha = np.pi / params["num_spokes"]
    theta0 = params["slope"] - alpha

    result = simulate(
        state0=[theta0, theta_dot_in],
        params=params,
        sim_time=sim_time_cap,
        model=model,
        max_step=0.01,
    )
    post = result["impact_states_post"]
    if len(post) == 0:
        return None
    return post[0, 1]


def estimate_floquet_multiplier(params, theta_star=None, eps=0.02):
    """Local slope of the return map at its fixed point, via a centered
    finite difference: perturb the post-impact theta_dot slightly on
    both sides and see how the next crossing responds."""
    if theta_star is None:
        _, theta_star = get_limit_cycle_theta_dot_star(params)

    plus = step_once(theta_star + eps, params)
    minus = step_once(theta_star - eps, params)
    if plus is None or minus is None:
        raise RuntimeError("Perturbed trajectory failed to impact -- reduce eps.")

    slope = (plus - minus) / (2 * eps)
    return slope, theta_star


# ---------------------------------------------------------------------
# 1) Return map plot
# ---------------------------------------------------------------------

def plot_return_map(params):
    post_theta_dots, theta_star = get_limit_cycle_theta_dot_star(params)

    theta_dot_n = post_theta_dots[:-1]
    theta_dot_next = post_theta_dots[1:]

    lo, hi = min(theta_dot_n.min(), theta_dot_next.min()), max(
        theta_dot_n.max(), theta_dot_next.max()
    )

    plt.figure(3)
    plt.plot(theta_dot_n, theta_dot_next, "o-", label="Return map data")
    plt.plot([lo, hi], [lo, hi], "k--", label="Identity line")
    plt.plot(theta_star, theta_star, "r*", markersize=15, label="Fixed point")
    plt.xlabel(r"$\dot\theta_i$ (post-impact)")
    plt.ylabel(r"$\dot\theta_{i+1}$ (post-impact)")
    plt.title(f"Return map (slope={params['slope']}, N={params['num_spokes']})")
    plt.legend()
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.1)

    return theta_star


# ---------------------------------------------------------------------
# 2) Sweeps: slope, and number of spokes
# ---------------------------------------------------------------------

def roa_fraction_rolling(params, n_theta=10, n_thetadot=10, sim_time=10.0):
    """Coarse RoA grid, returns the fraction of grid points that land in
    the rolling limit cycle -- a cheap scalar summary for sweep plots."""
    _, _, labels = compute_roa_grid(
        params, n_theta=n_theta, n_thetadot=n_thetadot, sim_time=sim_time
    )
    rolling_label = LABEL_TO_INT["rolling_limit_cycle"]
    return np.mean(labels == rolling_label)


def sweep_slope(slopes, base_params, coarse_grid=True):
    floquet_vals = []
    roa_vals = []
    for slope in slopes:
        params = dict(base_params)
        params["slope"] = slope
        print(f"slope = {slope:.3f}")
        try:
            fq, _ = estimate_floquet_multiplier(params)
        except RuntimeError:
            fq = np.nan
        floquet_vals.append(fq)

        if coarse_grid:
            roa_vals.append(roa_fraction_rolling(params))
        else:
            roa_vals.append(np.nan)

    return np.array(floquet_vals), np.array(roa_vals)


def sweep_num_spokes(spoke_counts, base_params, coarse_grid=True):
    floquet_vals = []
    roa_vals = []
    for n in spoke_counts:
        params = dict(base_params)
        params["num_spokes"] = n
        print(f"num_spokes = {n}")
        try:
            fq, _ = estimate_floquet_multiplier(params)
        except RuntimeError:
            fq = np.nan
        floquet_vals.append(fq)

        if coarse_grid:
            roa_vals.append(roa_fraction_rolling(params))
        else:
            roa_vals.append(np.nan)

    return np.array(floquet_vals), np.array(roa_vals)


if __name__ == "__main__":
    base_params = model.generate_params()
    base_params["slope"] = 0.08

    # --- Return map + fixed point ---
    theta_star = plot_return_map(base_params)

    # --- Floquet multiplier at this operating point ---
    fq, _ = estimate_floquet_multiplier(base_params, theta_star=theta_star)
    print(f"Floquet multiplier estimate: {fq:.4f}")
    print("(|multiplier| < 1 means the limit cycle is locally stable)")

    # --- Sweep slope ---
    # NOTE: coarse_grid=True calls the RoA grid at each slope -- this is
    # slow. Start with fewer slope values / smaller grid, then expand if
    # time allows.
    slopes = np.linspace(0.04, 0.16, 5)
    floquet_by_slope, roa_by_slope = sweep_slope(slopes, base_params, coarse_grid=True)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), num=4)
    axes[0].plot(slopes, floquet_by_slope, "o-")
    axes[0].set_xlabel("slope (rad)")
    axes[0].set_ylabel("Floquet multiplier")
    axes[0].set_title("Floquet multiplier vs slope")

    axes[1].plot(slopes, roa_by_slope, "o-")
    axes[1].set_xlabel("slope (rad)")
    axes[1].set_ylabel("fraction of grid -> rolling limit cycle")
    axes[1].set_title("RoA size vs slope")
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.1)

    # --- Sweep number of spokes ---
    spoke_counts = np.arange(6, 13)
    floquet_by_n, roa_by_n = sweep_num_spokes(
        spoke_counts, base_params, coarse_grid=True
    )

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), num=5)
    axes[0].plot(spoke_counts, floquet_by_n, "o-")
    axes[0].set_xlabel("number of spokes N")
    axes[0].set_ylabel("Floquet multiplier")
    axes[0].set_title("Floquet multiplier vs N")

    axes[1].plot(spoke_counts, roa_by_n, "o-")
    axes[1].set_xlabel("number of spokes N")
    axes[1].set_ylabel("fraction of grid -> rolling limit cycle")
    axes[1].set_title("RoA size vs N")
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(0.1)

    print("\nAll three figures are open -- close their windows when you're done viewing them.")
    plt.show()  # blocks here so all figures stay open until you close them