import numpy as np
import matplotlib.pyplot as plt

from models import rimless_wheel
from integrators import rk4, hybrid


def wheel_geometry(time_traj, state_traj, params):
    """Stance angle -> world coordinates.

    Returns hub (N,2), contact (N,2). x is horizontal, y is vertical, the
    ramp descends to the right. theta is the stance-leg angle from vertical,
    so hub = contact + length * (sin theta, cos theta).
    """
    length = params["length"]
    alpha = params["alpha"]
    ramp_angle = params["ramp_angle"]

    angle = state_traj[0]

    # Each impact moves the contact one chord down (or up) the ramp. The
    # chord between adjacent spoke tips is 2*l*sin(alpha).
    chord = 2 * length * np.sin(alpha)
    step_vec = chord * np.array([np.cos(ramp_angle), -np.sin(ramp_angle)])

    # Impacts appear in theta as a jump of -2*alpha (downhill) or +2*alpha
    # (uphill); flow never moves theta that far in one timestep.
    delta = np.diff(angle)
    direction = np.zeros_like(angle)
    direction[1:] = np.where(delta < -alpha, 1.0,
                    np.where(delta > alpha, -1.0, 0.0))
    step_count = np.cumsum(direction)

    contact = np.outer(step_count, step_vec)
    hub = contact + length * np.column_stack([np.sin(angle), np.cos(angle)])
    return hub, contact


def spoke_tips(hub_xy, angle, params):
    """All N spoke tips for the wheel posed with its stance leg at `angle`."""
    length = params["length"]
    alpha = params["alpha"]
    n = params["number_of_spokes"]

    phi = angle + 2 * alpha * np.arange(n)
    return hub_xy - length * np.column_stack([np.sin(phi), np.cos(phi)])


def plot_path(time_traj, state_traj, params, rest_time=None, n_poses=9):
    hub, contact = wheel_geometry(time_traj, state_traj, params)
    ramp_angle = params["ramp_angle"]

    # trim the frozen tail so the resting pose isn't drawn 50000 times
    stop = len(time_traj)
    if rest_time is not None:
        stop = min(stop, int(rest_time / (time_traj[1] - time_traj[0])) + 2)
    hub, contact, angle = hub[:stop], contact[:stop], state_traj[0][:stop]

    fig, ax = plt.subplots(figsize=(11, 5))

    # ramp surface
    x0, x1 = hub[:, 0].min() - 0.6, hub[:, 0].max() + 0.6
    ramp_y = [-np.tan(ramp_angle) * x0, -np.tan(ramp_angle) * x1]
    ax.plot([x0, x1], ramp_y, color="0.3", lw=2, zorder=1)
    ax.fill_between([x0, x1], ramp_y, -100, color="0.92", zorder=0)

    # the wheel drawn at a few instants, darkening with time
    idx = np.linspace(0, stop - 1, n_poses).astype(int)
    for j, i in enumerate(idx):
        tips = spoke_tips(hub[i], angle[i], params)
        shade = str(0.75 - 0.55 * j / max(len(idx) - 1, 1))
        for tip in tips:
            ax.plot([hub[i, 0], tip[0]], [hub[i, 1], tip[1]],
                    color=shade, lw=1.1, zorder=2)
        ax.plot(*hub[i], "o", color=shade, ms=4, zorder=3)

    ax.plot(hub[:, 0], hub[:, 1], color="tab:blue", lw=2,
            label="hub path", zorder=4)
    uniq = np.unique(np.round(contact, 9), axis=0)
    ax.plot(uniq[:, 0], uniq[:, 1], "v", color="tab:red", ms=7,
            label="contact points", zorder=5)

    if rest_time is not None:
        ax.plot(*hub[-1], "*", color="tab:green", ms=18,
                label=f"rest at t={rest_time:.3f}s", zorder=6)

    ax.set_aspect("equal")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title("Rimless wheel path on the slope")
    ax.legend(loc="upper right")
    ax.set_ylim(min(hub[:, 1].min(), ramp_y[1]) - 0.3, hub[:, 1].max() + 0.4)
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    params = rimless_wheel.generate_params()
    alpha, gamma = params["alpha"], params["ramp_angle"]

    for name, x0, T in [
        ("rolling", np.array([gamma - alpha, 2.2]), 3.0),
        ("resting", np.array([gamma - alpha + 0.30, -1.0]), 3.0),
    ]:
        t, s, rest = hybrid.integrate(rimless_wheel, rk4.step, 1e-4, T, x0, params)
        fig = plot_path(t, s, params, rest)
        fig.savefig(f"path_{name}.png", dpi=110)
    plt.show()