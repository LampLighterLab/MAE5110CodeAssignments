import numpy as np
import matplotlib.pyplot as plt
import timeit
from dataclasses import dataclass

from integrators import rk4 as integrator

#defining all the parameters here to use later on 
@dataclass
class WheelParams:
    N: int = 8            # number of spokes
    length: float = 1.0   # spoke length [m]
    g: float = 9.81        # gravity [m/s^2]
    gamma: float = 0.15    # ground slope [rad]

    # angle between each spoke
    @property
    def alpha(self):
        return np.pi / self.N


def dynamics(t, x, p: WheelParams):
    """
    Equation of motion for the continuous part is an inverted pendulum about the contact pt of the spoke
    """
    theta, thetadot = x
    thetaddot = (p.g / p.length) * np.sin(theta)
    return np.array([thetadot, thetaddot])


def forward_guard(p: WheelParams):
    """Handles the angle condition for when the front spoke is about to contact the ground"""
    def guard(t, x, p=p):
        return x[0] - (p.gamma + p.alpha)
    guard.direction = 1
    return guard


def backward_guard(p: WheelParams):
    """Handles the anglecondition for when we rock back onto the back spoke and stop the wheel"""
    def guard(t, x, p=p):
        return x[0] - (p.gamma - p.alpha)
    guard.direction = -1
    return guard


def reset(x, p: WheelParams):
    """Logic for switching coordinate frames and angular momentum conservation"""
    theta, thetadot = x
    return np.array([theta - 2 * p.alpha, thetadot * np.cos(2 * p.alpha)])


def integrate_to_guard(x0, guards, p: WheelParams, dt=0.001, t_max=10.0, bisect_tol=1e-10):
    """Use RK4 as the integrator until one of the guards is detected
    If this happens that means a collision is occuring so the timestep is decreased
    to gain more preciseness about that point."""
    x, t = np.array(x0, dtype=float), 0.0
    g_prev = [g(t, x) for g in guards] #the event guards (see methods above)
    while t < t_max:
        x_next = integrator.step(dynamics, t, x, dt, p)

        g_next = [g(t + dt, x_next) for g in guards]

        for i, g in enumerate(guards):

            crossed = (g_prev[i] < 0 <= g_next[i]) if g.direction == 1 \
                else (g_prev[i] >= 0 > g_next[i])
            if crossed:
                t_lo = t
                x_lo = x
                g_lo = g_prev[i]
                t_hi = t + dt
                x_hi = x_next
                while (t_hi - t_lo) > bisect_tol:
                    t_mid = 0.5 * (t_lo + t_hi)
                    x_mid = integrator.step(dynamics, t_lo, x_lo, t_mid - t_lo, p)
                    g_mid = g(t_mid, x_mid)

                    lo_side = (g_lo < 0) if g.direction == 1 else (g_lo >= 0)

                    mid_side = (g_mid < 0) if g.direction == 1 else (g_mid >= 0)

                    if lo_side == mid_side:
                        t_lo = t_mid
                        x_lo = x_mid
                        g_lo = g_mid
                    else:
                        t_hi = t_mid
                        x_hi = x_mid
                return t_hi, x_hi, i

        x = x_next
        t = t + dt

    return t, x, None


def simulate_one_stance(x0, p: WheelParams, dt=0.001, t_max=10.0):
    """calculates one step"""
    t_ev, x_ev, which = integrate_to_guard(
        x0, [forward_guard(p), backward_guard(p)], p, dt=dt, t_max=t_max
    )
    outcome = {0: "forward", 1: "backward", None: "timeout"}[which]
    return t_ev, x_ev, outcome


def simulate_steps(x0, p: WheelParams, n_steps=50, dt=0.001, t_max=10.0):
    """Go through multiple steps in sequence, calling simulate_one_stance each time"""
    x = np.array(x0, dtype=float)
    thetadot_pre = []
    thetadot_post = []
    outcome = "forward" #assume we are starting off here 

    for _ in range(n_steps):
        t_ev, x_impact, outcome = simulate_one_stance(x, p, dt=dt, t_max=t_max)

        if outcome != "forward":
            break #we know we are stopped so there is no more integration to be done
        thetadot_pre.append(x_impact[1]) #use this for limit cycle
        x = reset(x_impact, p)
        thetadot_post.append(x[1]) #use this for limit cycle

    return x, outcome, np.array(thetadot_pre), np.array(thetadot_post)


def energy(x, p: WheelParams):
    """calculate energy at any given point"""
    theta, thetadot = x
    return 0.5 * (p.length * thetadot) ** 2 + p.g * p.length * np.cos(theta)


def check_energy_conservation_within_stance():
    """used to check if energy is conserved up to the point of collision"""
    p = WheelParams(gamma=0.0)

    x0 = np.array([0.05, 0.5])

    x, t, dt = x0.copy(), 0.0, 0.001
    for _ in range(2000):  #2s so it will capture one stance 
        x = integrator.step(dynamics, t, x, dt, p)
        t += dt
    print(f"drift= {abs(energy(x, p) - energy(x0, p))} (expect ~0)")


def check_impact_energy_loss_ratio():
    """the ration should equal cos^2(2*alpha) every impact if the collision is working properly"""
    p = WheelParams(N=8, gamma=0.2)

    x0 = np.array([p.gamma - p.alpha + 0.01, 1.0])

    ex1, ex2, pre, post = simulate_steps(x0, p, n_steps=20)

    print(f"[check 2] expected KE ratio = {np.cos(2 * p.alpha) ** 2:.6f}, "
          f"actual (min/max over all impacts) = "
          f"{(post**2/pre**2).min():.6f} / {(post**2/pre**2).max():.6f}")


def classify_point(theta0, thetadot0, p: WheelParams, n_steps=20, dt=0.002, t_max=5.0):
    """if the outcome is 1 it converges to the rolling limit cycle otherwise if its is 0, the wheel falls over and stops"""
    ex1, outcome, ex2, ex3 = simulate_steps(np.array([theta0, thetadot0]), p, n_steps, dt, t_max)
    if outcome == "forward":
        return 1
    else:
        return 0


def sweep_roa(p: WheelParams, n_theta=30, n_thetadot=30, thetadot_range=(-4.0, 4.0),
              n_steps=20, dt=0.002, t_max=5.0):
    """setup method for plotting the regions of attractions for the graph"""
    thetas = np.linspace(p.gamma - p.alpha, p.gamma + p.alpha, n_theta)
    thetadots = np.linspace(*thetadot_range, n_thetadot)
    labels = np.array([[classify_point(th, td, p, n_steps, dt, t_max) for th in thetas]
                        for td in thetadots])
    return thetas, thetadots, labels


def plot_roa(thetas, thetadots, labels, p: WheelParams, ax=None):
    if ax is None:
        ex1, ax = plt.subplots(figsize=(6, 5))
    extent = [thetas[0], thetas[-1], thetadots[0], thetadots[-1]]
    ax.imshow(labels, origin="lower", extent=extent, aspect="auto", cmap="coolwarm", vmin=0, vmax=1)
    ax.set_xlabel("theta [rad]")
    ax.set_ylabel(r"$\dot\theta$ [rad/s]")
    ax.set_title(f"RoA: N={p.N}, $\\gamma$={p.gamma} rad (blue=falls, red=rolling)")
    return ax

def poincare_step(thetadot_post, p: WheelParams, dt=0.001, t_max=5.0):
    """Given the post-impact velocity we want to return the post-impact velocity"""
    x0 = np.array([p.gamma - p.alpha, thetadot_post])
    ex1, x_impact, outcome = simulate_one_stance(x0, p, dt=dt, t_max=t_max)

    if outcome == "forward":
        return reset(x_impact, p)[1]
    else:
        return None


def find_fixed_point_and_floquet(p: WheelParams, dtheta=1e-3, max_iter=50):
    """Finds the fixed point of the return map by just repeatedly applying the map
      until it stops changing and 
      Calculated the Floquet multiplier as the local slope at 
      that fixed point that it intersects with the y=x line"""
    thetadot_star = None
    for guess in [1.0, 2.0, 3.0, 4.0, 5.0]:
        td = guess
        for ex1 in range(max_iter):
            td_next = poincare_step(td, p)
            if td_next is None:
                break
            if abs(td_next - td) < 1e-6:
                thetadot_star = td_next
                break
            td = td_next
        if thetadot_star is not None:
            break

    if thetadot_star is None:
        return None, None

    f_plus = poincare_step(thetadot_star + dtheta, p)
    f_minus = poincare_step(thetadot_star - dtheta, p)
    if f_plus is None or f_minus is None:
        return thetadot_star, None

    floquet = (f_plus-f_minus) / (2 * dtheta)
    return thetadot_star, floquet


def trace_limit_cycle_trajectory(p: WheelParams, thetadot_star, dt=0.001, t_max=5.0):
    """Trace out the limit cycle trajectory"""
    x, t = np.array([p.gamma - p.alpha, thetadot_star]), 0.0
    fwd = forward_guard(p)
    thetas_traj, thetadots_traj = [x[0]], [x[1]]

    while t < t_max:
        x_next = integrator.step(dynamics, t, x, dt, p)
        if fwd(t + dt, x_next) >= 0:
            t_lo, x_lo, t_hi, x_hi = t, x, t + dt, x_next
            for _ in range(40):
                t_mid = 0.5 * (t_lo + t_hi)
                x_mid = integrator.step(dynamics, t_lo, x_lo, t_mid - t_lo, p)
                if fwd(t_mid, x_mid) < 0:
                    t_lo, x_lo = t_mid, x_mid
                else:
                    t_hi, x_hi = t_mid, x_mid
            thetas_traj.append(x_hi[0])
            thetadots_traj.append(x_hi[1])
            break
        x, t = x_next, t + dt
        thetas_traj.append(x[0])
        thetadots_traj.append(x[1])

    return np.array(thetas_traj), np.array(thetadots_traj)


def overlay_limit_cycle(ax, p: WheelParams, thetadot_star):
    """Draw the limit cycle trajectory and two fixed points on the ROA graph"""
    th_traj, thd_traj = trace_limit_cycle_trajectory(p, thetadot_star)
    ax.plot(th_traj, thd_traj, color="black", lw=2.0, label="stable limit cycle")
    ax.plot(th_traj[0], thd_traj[0], "o", color="lime", markeredgecolor="black",
            markersize=8, zorder=5, label=r"fixed point $\dot\theta^{+*}$")
    ax.plot(th_traj[-1], thd_traj[-1], "s", color="gold", markeredgecolor="black",
            markersize=8, zorder=5, label=r"fixed point $\dot\theta^{-*}$")
    ax.legend(loc="lower right", fontsize=8)


def compute_return_map(p: WheelParams, thetadot_range, n_points=80, dt=0.001, t_max=5.0):
    thetadots_in = np.linspace(*thetadot_range, n_points)
    thetadots_out = np.array([poincare_step(td, p, dt, t_max) or np.nan for td in thetadots_in])
    return thetadots_in, thetadots_out


def plot_return_map(thetadots_in, thetadots_out, fixed_point=None, ax=None):
    if ax is None:
        ex1, ax = plt.subplots(figsize=(6, 6))
    valid = ~np.isnan(thetadots_out)
    ax.plot(thetadots_in[valid], thetadots_out[valid], "-o", color="tab:blue",
            markersize=3, lw=1, label=r"$\dot\theta_{n+1}=f(\dot\theta_n)$")
    lims = [thetadots_in.min(), thetadots_in.max()]
    ax.plot(lims, lims, "k--", lw=1, label="identity line")
    if fixed_point is not None:
        ax.plot(fixed_point, fixed_point, "o", color="lime", markeredgecolor="black",
                markersize=10, zorder=5, label="fixed point")
    ax.set_xlabel(r"$\dot\theta_n^+$ [rad/s]")
    ax.set_ylabel(r"$\dot\theta_{n+1}^+$ [rad/s]")
    ax.set_title("Return map (Poincare section at impact)")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_aspect("equal", adjustable="box")
    return ax


def run_parameter_sweep(param_name, param_values, base_params=None,
                         n_theta=25, n_thetadot=25, thetadot_range=(-2.0, 4.0)):
    base_params = base_params or WheelParams()
    results = []
    for val in param_values:
        p = WheelParams(**{**base_params.__dict__, param_name: val})
        thetadot_star, floquet = find_fixed_point_and_floquet(p)
        thetas, thetadots, labels = sweep_roa(
            p, n_theta, n_thetadot, thetadot_range, n_steps=15, dt=0.002
        )
        results.append(dict(param_val=val, p=p, thetadot_star=thetadot_star,
                             floquet=floquet, roa_fraction=labels.mean(),
                             thetas=thetas, thetadots=thetadots, labels=labels))
        floquet_str = f"{floquet:.4f}" if floquet is not None else "no periodic orbit"
        print(f"  [{param_name}={val:.3g}] floquet={floquet_str}, "
              f"roa_fraction={labels.mean():.3f}")
    return results


def plot_roa_grid_comparison(results, param_label):
    """Compare multiple ROA graphs (like for the gamma sweep and the number of spokes sweep)"""
    n = len(results)
    fig, axes = plt.subplots(1, n, figsize=(4.2 * n, 4.2), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, r in zip(axes, results):
        plot_roa(r["thetas"], r["thetadots"], r["labels"], r["p"], ax=ax)
        if r["thetadot_star"] is not None:
            overlay_limit_cycle(ax, r["p"], r["thetadot_star"])
        ax.set_title(f"{param_label}={r['param_val']:.3g}")

    fig.tight_layout()
    return fig


def plot_sweep_metrics(results, param_label, analytic_floquet_fn=None):
    """See if the floquet number and the ROA percentage (of outcome) change as a function of the sweep variable"""
    vals = [r["param_val"] for r in results]
    floquets = [r["floquet"] if r["floquet"] is not None else np.nan for r in results]
    fractions = [r["roa_fraction"] for r in results]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    ax1.plot(vals, floquets, "o-", color="tab:blue", label="numerical")
    if analytic_floquet_fn is not None:
        vals_fine = np.linspace(min(vals), max(vals), 200)
        ax1.plot(vals_fine, [analytic_floquet_fn(v) for v in vals_fine], "--",
                  color="tab:red", label=r"analytic $\cos^2(2\alpha)$")
    ax1.axhline(1.0, color="k", lw=0.5, ls=":")
    ax1.set_xlabel(param_label)
    ax1.set_ylabel("Floquet multiplier")
    ax1.set_title("Local stability")
    ax1.legend(fontsize=8)

    ax2.plot(vals, fractions, "o-", color="tab:purple")
    ax2.set_xlabel(param_label)
    ax2.set_ylabel("fraction of grid rolling")
    ax2.set_title("RoA size")
    ax2.set_ylim(0, 1)

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    check_energy_conservation_within_stance()
    check_impact_energy_loss_ratio()

    #showing that it works for one spoke and gamma configuration
    p = WheelParams(N=8, gamma=0.2)
    x0 = np.array([p.gamma - p.alpha + 0.01, 1.0])
    x_final, outcome, pre, post = simulate_steps(x0, p, n_steps=30)
    print(f"\noutcome={outcome}, final state={x_final}")

    #baseline RoA and limit cycle plotting
    thetadot_star, floquet = find_fixed_point_and_floquet(p)
    thetas, thetadots, labels = sweep_roa(p, n_theta=30, n_thetadot=30)
    print(f"ROA: fraction rolling: {labels.mean():.3f}, floquet={floquet:.4f}")

    fig, ax = plt.subplots(figsize=(6, 5))
    plot_roa(thetas, thetadots, labels, p, ax=ax)
    overlay_limit_cycle(ax, p, thetadot_star)
    fig.tight_layout()
    fig.savefig("roa_demo.png", dpi=150)

    #return map
    thetadots_in, thetadots_out = compute_return_map(p, thetadot_range=(0.3, 3.0))
    fig2, ax2 = plt.subplots(figsize=(6, 6))
    plot_return_map(thetadots_in, thetadots_out, fixed_point=thetadot_star, ax=ax2)
    fig2.tight_layout()
    fig2.savefig("return_map_demo.png", dpi=150)

    #try to sweep across different gamma values for the slope angle
    print("\nGamma sweep")
    gamma_results = run_parameter_sweep(
        "gamma", [0.10, 0.15, 0.20, 0.25, 0.30], base_params=WheelParams(N=8)
    )
    plot_roa_grid_comparison(gamma_results, r"$\gamma$").savefig("sweep_gamma_roa.png", dpi=150)
    plot_sweep_metrics(
        gamma_results, r"slope $\gamma$ [rad]",
        analytic_floquet_fn=lambda g: np.cos(2 * np.pi / 8) ** 2
    ).savefig("sweep_gamma_metrics.png", dpi=150)

    #try to sweep across different spoke counts
    print("\nN sweep")
    N_results = run_parameter_sweep(
        "N", [6, 8, 10, 12], base_params=WheelParams(gamma=0.25)
    )
    plot_roa_grid_comparison(N_results, "N").savefig("sweep_N_roa.png", dpi=150)
    plot_sweep_metrics(
        N_results, "spoke count N",
        analytic_floquet_fn=lambda N: np.cos(2 * np.pi / N) ** 2
    ).savefig("sweep_N_metrics.png", dpi=150)

    print("\nAll graphs are made")