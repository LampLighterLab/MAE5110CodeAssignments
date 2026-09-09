import numpy as np
import matplotlib.pyplot as plt

# Run-location bootstrap: this script lives two levels below the workspace root,
# so plain `python assignments/assignment_1/assignment_1.py` would not find the
# top-level `models` / `integrators` packages without PYTHONPATH.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s][%(funcName)s] %(levelname)s %(name)s: %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Shared impact-event helpers: the model owns the guard locations, and every
# callback below must go through detect_impact so the literals cannot drift.
def detect_impact(state1, state2, params):
    """
    Detect a rimless-wheel impact inside one integration step.

    Composes the displacement/velocity-mismatch test (continuous flow obeys
    sign(theta2 - theta1) == sign(theta_dot), while a reset teleports theta
    by -/+2*alpha opposite to the motion) with a magnitude leg
    (|dtheta| > alpha) that rules out mid-step turnarounds and a pre-side
    check that localizes which guard was hit.

    Returns "forward", "backward", or None (no event).
    """
    alpha = params["alpha"]
    gamma = params["gamma"]
    guard_forward = alpha + gamma
    guard_backward = gamma - alpha

    theta1 = float(state1[0])
    theta_dot1 = float(state1[1])
    theta2 = float(state2[0])
    dtheta = theta2 - theta1

    if theta_dot1 > 0.0 and dtheta < -alpha and theta1 < guard_forward:
        return "forward"
    if theta_dot1 < 0.0 and dtheta > alpha and theta1 > guard_backward:
        return "backward"

    # Health check: crossed a guard location with no teleport. With the
    # fixed integrator this should not happen; it means a reset went missing.
    # if theta_dot1 > 0.0 and theta1 < guard_forward <= theta2:
    #     logger.warning("detect_impact: crossed forward guard without discrete jump.")
    # elif theta_dot1 < 0.0 and theta1 > guard_backward >= theta2:
    #     logger.warning("detect_impact: crossed backward guard without discrete jump.")
    return None

from integrators import integrator_rk4
from models import model_rimless_wheel
from plot_helpers.plot_energy import plot_energy
from plot_helpers.plot_phase import plot_phase

def analytical_fix_point(gamma: float, alpha: float, g: float, length: float):
    """
    Compute the analytical fix point for the rimless wheel given the parameters.
    """
    theta_dot_fix_point = 2 * np.sqrt(g * np.sin(alpha) * np.sin(gamma) / (length * (1 - np.cos(2 * alpha) ** 2)))
    state_fix_point = np.array([gamma + alpha, theta_dot_fix_point]) # theta/theta_dot fix point
    return state_fix_point

def plot_sim(final_time: float, sampling_period: float, state_0: np.ndarray, integrator_params: dict, model_params: dict, if_energy_test: bool = True, if_plot: bool = True, fig_dir: str = ""):
    # 1. Create models and integrators
    model = model_rimless_wheel.ModelRimlessWheel()
    integrator = integrator_rk4.IntegratorRK4()

    # 2. Set up initial conditions and parameters
    model.set_params(model_params)

    # 3. Run the simulation
    t0 = 0.0
    time_trajectory = np.arange(t0, final_time, sampling_period)
    state_trajectory = integrator.integrate(
        param_integrator=integrator_params,
        param_model=model_params,
        time_trajectory=time_trajectory,
        initial_state=state_0,
        model=model,
        checkpoint_callback=None # impact_event_guard
    )

    # 4. Sanity check: the energy should be constant
    if if_energy_test:
        potential, kinetic = model.calculate_energy(state_trajectory)
        total_energy = potential + kinetic
        energy_variation = np.max(total_energy) - np.min(total_energy)
        logger.info(f"Energy variation over the trajectory: {energy_variation:.6f}")
        if energy_variation > 1e-2:
            logger.warning("Energy is not conserved! Check the integrator or model implementation.")

    # 5. Plots
    if not if_plot:
        return
    # an 2x1 subplot
    fig, (ax1, ax2) = plt.subplots(2, 1)
    #   4.1. Print Energies
    plot_param = {
        "title": "Rimless Wheel Energy vs Time",
        "xlabel": "Time (s)",
        "ylabel": "Energy (J)"
    }
    ax1 = plot_energy(time_trajectory, state_trajectory, model, ax=ax1, plot_param=plot_param)

    #   4.2. Phase Portrait
    plot_param = {
        "title": "Rimless Wheel Phase Portrait",
        "xlabel": "Theta (rad)",
        "ylabel": "Theta dot (rad/s)",
        "state1_index": 0,
        "state2_index": 1
    }
    ax2 = plot_phase(state_trajectory, ax=ax2, plot_param=plot_param)

    #   4.3. Show the plots
    plt.tight_layout()
    if fig_dir != "":
        plt.savefig(fig_dir + "/rimless_wheel_simulation.png")
    else:
        plt.show()

def analysis(sampling_period: float, integrator_params: dict, model_params: dict, if_RoA_analysis: bool = True, fig_dir: str = ""):
    # 1. Create models and integrators
    model = model_rimless_wheel.ModelRimlessWheel()
    integrator = integrator_rk4.IntegratorRK4()

    # 2. Set up initial conditions and parameters
    model.set_params(model_params)

    gamma = model_params["gamma"]
    alpha = model_params["alpha"]
    g = model_params["g"]
    length = model_params["length"]
    alpha = model_params["alpha"]

    t0 = 0.0
    tf = 10.0
    dt = sampling_period

    # close form limit cycle solution:
    state_fix_point = analytical_fix_point(gamma=gamma, alpha=alpha, g=g, length=length)

    if if_RoA_analysis:
        # 3. RoA analysis
        # _, ax = plt.subplots()
        # 3.1. Making grids
        theta_min = gamma - alpha
        theta_max = gamma + alpha
        theta_dot_min = -4
        theta_dot_max = 4
        num_points = 11
        theta_grid = np.linspace(theta_min, theta_max, num_points)
        theta_dot_grid = np.linspace(theta_dot_min, theta_dot_max, num_points)
        last_forward_theta_dots = np.zeros((num_points, num_points))
        # 3.2. cluster the last forward transition event using theta_dot
        i = 0
        for theta in theta_grid:
            j = 0
            for theta_dot in theta_dot_grid:
                state_0 = np.array([theta, theta_dot])
                time_trajectory = np.arange(t0, tf, dt)

                # callback recording the last forward transition event's post-impact state
                last_forward_state = None
                def checkpoint_callback(t1, state1, t2, state2, model):
                    nonlocal last_forward_state
                    if detect_impact(state1, state2, model.get_params()) == "forward":
                        last_forward_state = state2
                
                state_trajectory = integrator.integrate(
                    param_integrator=integrator_params,
                    param_model=model_params,
                    time_trajectory=time_trajectory,
                    initial_state=state_0,
                    model=model,
                    checkpoint_callback=checkpoint_callback # impact_event_guard
                )

                if last_forward_state is not None:
                    last_forward_theta_dots[i, j] = last_forward_state[1]
                else:
                    last_forward_theta_dots[i, j] = np.nan # no forward transition event occurred

                j += 1

            i += 1
        # 3.3. Cluster last forward theta dot using dbscan
        from sklearn.cluster import DBSCAN
        # Reshape the data for clustering
        X = last_forward_theta_dots.flatten().reshape(-1, 1)
        initial_states = np.array([[theta, theta_dot] for theta in theta_grid for theta_dot in theta_dot_grid])
        # Remove NaN values for clustering for both X and initial_states
        valid_indices = ~np.isnan(X.flatten())
        X_valid = X[valid_indices]
        initial_states_valid = initial_states[valid_indices.flatten()]
        # Perform DBSCAN clustering
        dbscan = DBSCAN(eps=0.1, min_samples=2)
        clusters = dbscan.fit_predict(X_valid)
        # 3.4. Plot the clusters with a discrete colorbar (one tick per cluster label)
        import matplotlib as mpl
        unique_labels = np.unique(clusters)
        num_labels = len(unique_labels)
        cmap = plt.get_cmap('viridis', num_labels)  # discrete LUT, not a continuous map
        lut_index = np.searchsorted(unique_labels, clusters)  # raw label -> 0..num_labels-1
        norm = mpl.colors.BoundaryNorm(np.arange(num_labels + 1) - 0.5, num_labels)  # type: ignore
        padx = 0.1
        pady = 0.5
        plt.figure(figsize=(8, 6))
        sc = plt.scatter(initial_states_valid[:, 0], initial_states_valid[:, 1], c=lut_index, cmap=cmap, norm=norm, marker='o')
        cbar = plt.colorbar(sc, ticks=np.arange(num_labels))
        cbar.ax.set_yticklabels(['noise' if lab == -1 else f"{lab}" for lab in unique_labels])
        cbar.set_label('Cluster Label')
        plt.title('DBSCAN Clustering of Last Forward Theta Dot')
        plt.xlabel('Theta (rad)')
        plt.ylabel('Theta Dot (rad/s)')
        plt.xlim(theta_min - padx, theta_max + padx)
        plt.ylim(theta_dot_min - pady, theta_dot_max + pady)
        plt.grid()
        plt.tight_layout()
        if fig_dir != "":
            plt.savefig(fig_dir + "/rimless_wheel_RoA_analysis.png")
        else:
            plt.show()

    # 4. Numerical fix point by Poincare section
    # 4.1. Purturb the analytical fix point and see if it converges back to the fix point
    theta_perturb = 0.0
    theta_dot_perturb = 2.0
    dt = 1e-2
    state_perturbed = np.array([state_fix_point[0] + theta_perturb, state_fix_point[1] + theta_dot_perturb])
    time_trajectory = np.arange(t0, tf, dt)
    # 4.2. lambda callback recording forward transition theta dot jump
    theta_dot_jumps: list[list[float]] = [] # list of list [theta_dot_before_jump, theta_dot_after_jump]
    pre_image = None
    def checkpoint_callback(t1, state1, t2, state2, model):
        nonlocal pre_image
        if detect_impact(state1, state2, model.get_params()) == "forward":
            if pre_image is not None:
                pre = pre_image
                post = state1
                theta_dot_jumps.append([pre[1], post[1]])
            pre_image = state1
    # 4.3. Run the simulation
    state_trajectory = integrator.integrate(
        param_integrator=integrator_params,
        param_model=model_params,
        time_trajectory=time_trajectory,
        initial_state=state_perturbed,
        model=model,
        checkpoint_callback=checkpoint_callback # impact_event_guard
    )
    # 4.4. Plot the theta dot jumps and compare with x=y line as well as the analytical fix point
    if len(theta_dot_jumps) == 0:
        logger.warning("No forward transition events recorded; skipping theta-dot jump map.")
        return  # NOTE: analysis() ends here; move this guard if section 5 is added below
    theta_dot_jumps_np: np.ndarray = np.array(theta_dot_jumps)
    record_jump_min = np.min(theta_dot_jumps)
    record_jump_max = np.max(theta_dot_jumps)
    pad = 0.01
    plt.figure(figsize=(8, 6))
    plt.scatter(theta_dot_jumps_np[:, 0], theta_dot_jumps_np[:, 1], label='Theta Dot Jumps', color='blue') # type: ignore
    plt.plot([record_jump_min, record_jump_max], [record_jump_min, record_jump_max], 'g--', label='y=x line')
    plt.plot(state_fix_point[1], state_fix_point[1], color='red', marker='*', markersize=12, label='Analytical Fix Point')
    plt.title('Theta Dot Jumps at Forward Transition')
    plt.xlabel('Theta Dot Before Jump (rad/s)')
    plt.ylabel('Theta Dot After Jump (rad/s)')
    plt.xlim(record_jump_min - pad, record_jump_max + pad)
    plt.ylim(record_jump_min - pad, record_jump_max + pad)
    plt.legend()
    plt.grid()
    plt.tight_layout()

    # 5. Floquent multipliers
    # compute (post - analytical_fix_point) / (pre - analytical_fix_point) for each jump and print the ratio
    ratios = abs(theta_dot_jumps_np[:, 1] - state_fix_point[1]) / abs(theta_dot_jumps_np[:, 0] - state_fix_point[1])
    for i, ratio in enumerate(ratios):
        print(f"Jump {i}: {ratio:.2f}")

    if fig_dir != "":
        plt.savefig(fig_dir + "/rimless_wheel_theta_dot_jump_map.png")
    else:
        plt.show()

def main():
    model = model_rimless_wheel.ModelRimlessWheel()
    model_params = model.generate_params()
    gamma = model_params["gamma"]
    alpha = model_params["alpha"]
    g = model_params["g"]
    length = model_params["length"]
    # 1. energy test with initial condition at the analytical fix point
    state_fix_point = analytical_fix_point(gamma=gamma, alpha=alpha, g=g, length=length)
    plot_sim(state_0=state_fix_point, params=model_params, if_energy_test=True, if_plot=False)

    # 2. plot the under speed test
    # state_under_speed = np.array([gamma + alpha , 0.01 * state_fix_point[1]])
    # plot_sim(state_0=state_under_speed, params=model_params, if_energy_test=False, if_plot=True)

    # 3. analysis
    # analysis(gamma=gamma, num_spokes=6)
    # analysis(gamma=gamma*2, num_spokes=4)

    # perturbation state plot
    model_params["gamma"] = np.pi / 10
    model_params["alpha"] = np.pi / 8
    state_fix_point = analytical_fix_point(gamma=model_params["gamma"], alpha=model_params["alpha"], g=g, length=length)
    state_perturbed = np.array([state_fix_point[0] , 0.1 * state_fix_point[1]])
    plot_sim(state_0=state_perturbed, params=model_params, if_energy_test=False, if_plot=True)

if __name__ == "__main__":
    main()