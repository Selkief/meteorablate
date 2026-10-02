"""Plot configurable speed families with the paper's model and conventions."""

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np


def make_profiles(module):
    velocities = module.FIGURE1_VELOCITIES_KM_S
    angles = module.FIGURE1_ENTRY_ELEVATION_ANGLES_DEG
    styles = ["-", "--", ":", "-.", (0, (5, 1, 1, 1)), (0, (3, 1, 1, 1, 1, 1))]
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    fig, axes = plt.subplots(2, 2, figsize=(9, 6.5), sharey=True, constrained_layout=True)
    axes = axes.ravel()
    peak_rates = []
    for j, angle in enumerate(angles):
        for k, velocity in enumerate(velocities):
            result = module.simulate_case(velocity, 1., angle)
            for axis, key in zip(axes, ("velocity_km_s", "mass_loss_rate_kg_s", "temperature_k", "mass_kg")):
                axis.plot(result[key], result["altitude_km"], color=colors[j],
                          linestyle=styles[k % len(styles)], lw=1.7)
            peak_rates.append(np.nanmax(result["mass_loss_rate_kg_s"]))
    axes[0].set_xlabel(r"Velocity [km s$^{-1}$]")
    axes[1].set_xlabel(r"Absolute mass-loss rate, $|dm/dt|$ [kg s$^{-1}$]")
    axes[2].set_xlabel("Temperature [K]")
    axes[3].set_xlabel("Mass [kg]")
    for i, axis in enumerate(axes):
        axis.set_ylim(70, 130)
        axis.set_title(("(a) Velocity", "(b) Mass loss rate", "(c) Temperature", "(d) Mass")[i])
        axis.grid(True, which="both", alpha=.25)
    for axis in (axes[0], axes[2]):
        axis.set_ylabel("Altitude [km]")
    axes[1].set_xscale("log")
    axes[1].set_xlim(min(peak_rates)/10, max(peak_rates)*10)
    axes[3].set_xscale("log")
    axes[0].legend(handles=[Line2D([0], [0], color=colors[j], label=rf"$\alpha={angle:g}^\circ$")
                           for j, angle in enumerate(angles)], title="Entry elevation", frameon=False, loc="upper left")
    axes[1].legend(handles=[Line2D([0], [0], color=".2", linestyle=styles[k % len(styles)],
                                 label=rf"{v:g} km s$^{{-1}}$") for k, v in enumerate(velocities)],
                   title="Entry speed", frameon=False, loc="lower right", fontsize=9)
    fig.savefig(module.FIG_DIR / "meteor_ablation_single_column.pdf")
    plt.close(fig)
