import numpy as np
import matplotlib.pyplot as plt

from models import rimless_wheel as model
from roa_sweep import compute_roa_grid

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
for ax, gamma in zip(axes, [0.1, 0.2, 0.4]):
    params = model.generate_params(num_spokes=8, slope_angle=gamma)
    alpha = params["half_spoke_angle"]
    theta_range = (gamma - alpha, alpha + gamma)
    theta_vals, theta_dot_vals, classification = compute_roa_grid(
        params, theta_range, (-4.0, 4.0), grid_size=40
    )
    ax.pcolormesh(theta_vals, theta_dot_vals, classification, shading="auto", cmap="coolwarm")
    ax.set_xlabel("θ (rad)")
    ax.set_ylabel("θ̇ (rad/s)")
    ax.set_title(f"γ={gamma:.2f} rad (N=8)")
plt.tight_layout()
plt.savefig("/mnt/user-data/outputs/roa_vs_gamma.png", dpi=150)
print("Saved RoA-vs-gamma comparison.")

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
for ax, N in zip(axes, [6, 8, 12]):
    params = model.generate_params(num_spokes=N, slope_angle=0.2)
    alpha = params["half_spoke_angle"]
    gamma = params["slope_angle"]
    theta_range = (gamma - alpha, alpha + gamma)
    theta_vals, theta_dot_vals, classification = compute_roa_grid(
        params, theta_range, (-4.0, 4.0), grid_size=40
    )
    ax.pcolormesh(theta_vals, theta_dot_vals, classification, shading="auto", cmap="coolwarm")
    ax.set_xlabel("θ (rad)")
    ax.set_ylabel("θ̇ (rad/s)")
    ax.set_title(f"N={N} (γ=0.2 rad)")
plt.tight_layout()
plt.savefig("/mnt/user-data/outputs/roa_vs_N.png", dpi=150)
print("Saved RoA-vs-N comparison.")