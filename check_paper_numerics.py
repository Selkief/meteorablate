"""Check sensitivity of three representative archived cases to halving max_step.

Run after reproduce_paper.py. This changes a numerical setting for the checks
only; it does not replace the paper's reproduced figures or table.
"""

import argparse
import importlib.util
from pathlib import Path
import sys

import h5py
import matplotlib
matplotlib.use("Agg")
import numpy as np

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--ablate-dir", type=Path, default=ROOT.parent / "ablate")
args = parser.parse_args()
sys.path.insert(0, str(args.ablate_dir / "src"))
source = ROOT / "paper/make_cabmod_figures.py"
if not source.exists():
    source = ROOT / "make_cabmod_figures.py"
spec = importlib.util.spec_from_file_location("paper_generator", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
original_build = module.build_kero_model


def build(*a, **kw):
    model = original_build(*a, **kw)
    model.config.set("integrate", "max_step_size_sec", "0.025")
    return model


module.build_kero_model = build
with h5py.File(ROOT / "reproduction/paper_results.h5", "r") as reference, h5py.File(
    ROOT / "reproduction/numerical_checks.h5", "w"
) as checks:
    checks.attrs["check"] = "Halve maximum RK45 step from 0.05 to 0.025 s; retain default tolerances"
    checks.create_dataset("check_source", data=Path(__file__).read_text())
    for velocity in (32., 52., 72.):
        group = next(g for g in reference["trajectories"].values()
                     if g.attrs["entry_velocity_km_s"] == velocity
                     and g.attrs["density_scale"] == 1.0 and g.attrs["elevation_deg"] == 45.)
        result = module.simulate_case(velocity, 1.0, 45.)
        original_peak = group.attrs["peak_altitude_km"]
        new_peak = result["peak_altitude_km"]
        output = checks.create_group(f"velocity_{velocity:.0f}")
        output.attrs.update({"velocity_km_s": velocity, "original_peak_km": original_peak,
                             "half_step_peak_km": new_peak, "peak_difference_km": new_peak-original_peak})
        for name, value in result.items():
            output.create_dataset(name, data=value)
        print(f"{velocity:g} km/s, gamma=1, elevation=45 deg: "
              f"{original_peak:.6f} -> {new_peak:.6f} km (change {new_peak-original_peak:+.6f} km)", flush=True)
