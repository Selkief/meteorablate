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
#ENTRY_ELEVATION_ANGLES_DEG = np.array([45.0], dtype=np.float64)


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
    for entry_elevation_angle_deg in ENTRY_ELEVATION_ANGLES_DEG:
        for velocity_km_s in VELOCITIES_KM_S:
            #1.0 stands for the density scale, constant for now
            key = (velocity_km_s, 1.0, entry_elevation_angle_deg)
            if key not in cache:
                if not cache_used:
                    print(f"simulating {key}")
                    cache_used = True

                cache[key] = cabmod.simulate_case(
                    velocity_km_s,
                    density_scale=1.0,
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
                    "entry_elevation_angle_deg": entry_elevation_angle_deg,
                    "velocity_km_s0": velocity_km_s,
                    "data": cache[key],
                }
            )
    return results

def get_h0(results_list):
    #compute altitude of peak mass loss for each velocity and angle
    #plot said altitude vs velocity for all angles
    data_by_angle = {
        angle: {"velocity": [], "h0": []}
        for angle in ENTRY_ELEVATION_ANGLES_DEG
    }
    for item in results_list:
        angle = item["entry_elevation_angle_deg"]
        altitude = item["data"]["altitude_km"]
        mass_loss_rate = item["data"]["mass_loss_rate_kg_s"]

        peak_massloss_index = np.argmax(mass_loss_rate)
        #peak_massloss = mass_loss_rate[peak_massloss_index]
        h0 = altitude[peak_massloss_index]

        data_by_angle[angle]["velocity"].append(item["velocity_km_s0"])
        data_by_angle[angle]["h0"].append(h0)

    for angle, data in data_by_angle.items():
        plt.scatter(data["velocity"], data["h0"], label=f"{angle}deg")
    plt.xlabel("velocity [km/s]")
    plt.ylabel("Altitude [km]")
    plt.grid()
    plt.legend(title="entry angle")
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