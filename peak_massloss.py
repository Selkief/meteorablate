import make_cabmod_figures as cabmod
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import pickle

ROOT = Path(__file__).resolve().parent
FIG_DIR = ROOT / "figures"
CACHE_FILE = ROOT/ "simulation_cache.pkl"

VELOCITIES_KM_S = np.arange(11.0, 72.0, 1)
ENTRY_ELEVATION_ANGLES_DEG = np.array([70.0, 45.0, 20.0], dtype=np.float64)
DENSITY_SCALES = np.array([0.8, 1.0, 1.2], dtype=np.float64)

density_styles = {0.8: "o", 1.0: "^", 1.2: "s"}
velocity_colours = {70.0: "tab:red", 45.0: "tab:blue", 20.0:"tab:green"}



def load_cache():
    #load data that has already been simulated instead of simulating each time
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)

    return {}


def sweep_velocities():
    #simulate meteor ablation for velocities and entry angles in the defined range
    #or load results if they already exist in cache
    cache = load_cache()
    cache_used = False
    results = []
    for density_scale in DENSITY_SCALES:
        for entry_elevation_angle_deg in ENTRY_ELEVATION_ANGLES_DEG:
            for velocity_km_s in VELOCITIES_KM_S:

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

def get_h0(results_list):
    #compute altitude of peak mass loss for each velocity and angle and for scaled neutral densities
    #plot said altitude vs velocity for all angles and different neutral densities
    #different angles will get different colours and different neutral densities different marker styles 
    #TO DO: add (non-confusing simple) legend!!
    
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

        plt.scatter(item["velocity_km_s0"], h0, marker=density_styles[density], fc = facecolour, edgecolors= velocity_colours[angle])
    plt.xlabel("velocity [km/s]")
    plt.ylabel("Altitude [km]")
    plt.grid()
    #plt.legend(title="entry angle")
    plt.savefig(FIG_DIR / "peak_massloss_hist2.png")
    plt.close()

def main():
    result = sweep_velocities()
    get_h0(result)


if __name__ == "__main__":
    main()


###find out why the curve goes up for small velocities? plot parameters!
##look at Maarsy data, find entry angle distribution
##extract initial detection height for each velocity from maarsy data