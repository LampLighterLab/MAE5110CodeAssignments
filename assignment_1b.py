import numpy as np
import matplotlib.pyplot as plt

from models import rimless_wheel as model
from simulate import simulate

# ---------------------------------------------------------------------
# Fixed slope for this RoA map (the sweep-over-slope part comes later)
# ---------------------------------------------------------------------
params = model.generate_params()
params["slope"] = 0.08


def classify_attractor(result, converge_tol=1e-2, tail=5, backward_threshold=-np.pi):
    """Classify the long-term behavior of one simulated trajectory.

    Returns one of:
      "rolling_limit_cycle" -- impacts settle into a repeating theta_dot
      "libration"           -- never impacts, oscillates in the well
      "falls_backward"      -- theta runs away negative, never impacts forward
      "unclassified"        -- impacted, but hasn't converged by sim_time
    """
    impacts = result["impact_states_post"]
    theta_final = result["state"][0, -1]

    if len(impacts) == 0:
        if theta_final < backward_threshold:
            return "falls_backward"
        return "libration"

    tail_vals = impacts[-tail:, 1] if len(impacts) >= tail else impacts[:, 1]
    if np.std(tail_vals) < converge_tol:
        return "rolling_limit_cycle"
    return "unclassified"


LABELS = ["falls_backward", "libration", "rolling_limit_cycle", "unclassified"]
LABEL_TO_INT = {name: i for i, name in enumerate(LABELS)}


def compute_roa_grid(params, n_theta=25, n_thetadot=25, sim_time=15.0, max_step=0.05):
    """Grid over (theta, theta_dot), simulate from every point, and
    classify which attractor it converges to."""
    alpha = np.pi / params["num_spokes"]

    theta_vals = np.linspace(-np.pi, np.pi, n_theta)
    thetadot_vals = np.linspace(-4.0, 4.0, n_thetadot)

    labels = np.zeros((n_theta, n_thetadot), dtype=int)

    total = n_theta * n_thetadot
    count = 0
    for i, theta0 in enumerate(theta_vals):
        for j, thetadot0 in enumerate(thetadot_vals):
            result = simulate(
                state0=[theta0, thetadot0],
                params=params,
                sim_time=sim_time,
                model=model,
                max_step=max_step,
            )
            label_name = classify_attractor(result)
            labels[i, j] = LABEL_TO_INT[label_name]

            count += 1
            if count % 50 == 0:
                print(f"  {count}/{total} grid points done")

    return theta_vals, thetadot_vals, labels


def find_limit_cycle_point(params, theta_dot0=2.5, sim_time=20.0, tail=5):
    """Run one long simulation to find the rolling limit cycle's steady
    post-impact (theta, theta_dot), so it can be marked on the RoA map."""
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
        return None  # never impacted -- can't mark a limit cycle here

    theta_dot_star = np.mean(post_theta_dots[-tail:])
    theta_star = params["slope"] - alpha  # standard post-impact angle
    return theta_star, theta_dot_star


if __name__ == "__main__":
    # NOTE: start small (e.g. n_theta=15, n_thetadot=15, sim_time=8.0) to
    # check everything works before committing to a slow, fine grid.
    theta_vals, thetadot_vals, labels = compute_roa_grid(
        params, n_theta=25, n_thetadot=25, sim_time=15.0
    )

    plt.figure(2)
    mesh = plt.pcolormesh(
        theta_vals, thetadot_vals, labels.T, shading="nearest", cmap="viridis"
    )
    cbar = plt.colorbar(mesh, ticks=range(len(LABELS)))
    cbar.ax.set_yticklabels(LABELS)

    limit_cycle_point = find_limit_cycle_point(params)
    if limit_cycle_point is not None:
        theta_star, theta_dot_star = limit_cycle_point
        plt.plot(
            theta_star,
            theta_dot_star,
            "r*",
            markersize=15,
            label="Rolling limit cycle (fixed point)",
        )
        plt.legend(loc="upper right")

    plt.xlabel("theta (rad)")
    plt.ylabel("theta_dot (rad/s)")
    plt.title(f"Rimless wheel RoA map (slope = {params['slope']})")
    plt.tight_layout()
    plt.show()