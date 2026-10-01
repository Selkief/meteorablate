import make_cabmod_figures as cabmod
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import pickle

ROOT = Path(__file__).resolve().parent
FIG_DIR = ROOT / "figures"
CACHE_FILE = ROOT/ "simulation_cache.pkl"

VELOCITIES_KM_S_RANGE = np.arange(22.0, 72.0, 1)
VELOCITIES_KM_S = np.array([22.0, 52.0, 72.0])
ENTRY_ELEVATION_ANGLES_DEG = np.array([70.0, 45.0, 20.0], dtype=np.float64)
DENSITY_SCALES = np.array([0.7, 1.0, 1.3], dtype=np.float64)
DENSITY_CST = np.array([1.0], dtype=np.float64)

density_styles = {0.7: "o", 1.0: "^", 1.3: "s"}
velocity_colours = {70.0: "tab:red", 45.0: "tab:blue", 20.0:"tab:green"}
velocity_linestyles = {22.0: "-", 32.0: "-", 52.0:"--", 72.0: ":"}



def load_cache():
    #load data that has already been simulated instead of simulating each time
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)

    return {}


def simulate_sabmod(densitie_scales, elevation_angles, velocities):
    #simulate meteor ablation for velocities and entry angles in the defined range
    #or load results if they already exist in cache
    cache = load_cache()
    cache_used = False
    results = []
    for density_scale in densitie_scales:
        for entry_elevation_angle_deg in elevation_angles:
            for velocity_km_s in velocities:

                key = (velocity_km_s, density_scale, entry_elevation_angle_deg)
                if key not in cache:
                    if not cache_used:
                        print(f"simulating {key}")
                        cache_used = True

                    cache[key] = cabmod.simulate_case(
                        velocity_km_s,
                        density_scale=density_scale,
                        entry_elevation_angle_deg=entry_elevation_angle_deg,
                    )
                    with open(CACHE_FILE, "wb") as f:
                        pickle.dump(cache, f)

                else:
                    if not cache_used:
                        print(f"Using cached results")
                        cache_used = True

                results.append(
                    {
                        "density_scale": density_scale,
                        "entry_elevation_angle_deg": entry_elevation_angle_deg,
                        "velocity_km_s0": velocity_km_s,
                        "data": cache[key],
                    }
                )
    return results

def reproduce_figures(result_list, fig_name):
    fig, axs = plt.subplots(2,2, figsize=(7.2, 5.4))
    for item in result_list:
        angle = item["entry_elevation_angle_deg"]
        density = item["density_scale"]
        altitude = item["data"]["altitude_km"]
        mass_loss_rate = item["data"]["mass_loss_rate_kg_s"]
        velocity = item["velocity_km_s0"]

        #axs[0,0].plot(item["velocity_km_s0"], altitude )
        axs[0,1].plot(mass_loss_rate, altitude, color=velocity_colours[angle], ls = velocity_linestyles[velocity])
        axs[1,0].plot(item["data"]["temperature_k"], altitude, color=velocity_colours[angle], ls = velocity_linestyles[velocity])
        axs[1,1].plot(item["data"]["mass_kg"], altitude, color=velocity_colours[angle], ls = velocity_linestyles[velocity])
    axs[0,1].set_xlabel("mass_loss_rate [kg/s]")
    axs[0,1].set_xscale("log")
    axs[0,1].set_xlim(1e-9, 1e-6)
    axs[0,1].set_ylabel("Altitude [km]")
    axs[0,1].set_ylim(70, 130)
    axs[0,1].grid()

    axs[1,0].set_xlabel("Temperature [K]")
    axs[1,0].set_ylabel("Altitude [km]")
    axs[1,0].grid()

    axs[1,1].set_xlabel("Mass [kg]")
    axs[1,1].set_ylabel("Altitude [km]")
    axs[1,1].set_xscale("log")
    axs[1,1].grid()
    #plt.legend(title="entry angle")
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"{fig_name}.png")
    plt.close()


def get_h0(results_list, fig_name):
    #compute altitude of peak mass loss for each velocity and angle and for scaled neutral densities
    #plot said altitude vs velocity for all angles and different neutral densities
    #different angles will get different colours and different neutral densities different marker styles 
    #TO DO: add (non-confusing simple) legend!!
    fig, axs = plt.subplots(1,1)
    for item in results_list:
        angle = item["entry_elevation_angle_deg"]
        density = item["density_scale"]
        altitude = item["data"]["altitude_km"]
        mass_loss_rate = item["data"]["mass_loss_rate_kg_s"]

        peak_massloss_index = np.argmax(mass_loss_rate)
        #peak_massloss = mass_loss_rate[peak_massloss_index]
        h0 = altitude[peak_massloss_index]

        if density == 1.0:
            facecolour = velocity_colours[angle]
        else:
            facecolour = "none"

        #axs[0].plot(mass_loss_rate, altitude, color=velocity_colours[angle])
        axs.scatter(item["velocity_km_s0"], h0, marker=density_styles[density], fc = facecolour, edgecolors= velocity_colours[angle])
    axs.set_xlabel("velocity [km/s]")
    axs.set_ylabel("Altitude [km]")
    axs.grid()
    #plt.legend(title="entry angle")
    plt.savefig(FIG_DIR / f"{fig_name}.png")
    plt.close()

def main():
    sweep_velocities = simulate_sabmod(DENSITY_SCALES, ENTRY_ELEVATION_ANGLES_DEG, VELOCITIES_KM_S_RANGE)
    reproduce = simulate_sabmod(DENSITY_CST, ENTRY_ELEVATION_ANGLES_DEG, VELOCITIES_KM_S)
    get_h0(sweep_velocities, "detection_veloc_alt")
    reproduce_figures(reproduce, "paper_figures")


if __name__ == "__main__":
    main()


###find out why the curve goes up for small velocities? plot parameters!
##look at Maarsy data, find entry angle distribution
##extract initial detection height for each velocity from maarsy data