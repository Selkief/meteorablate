"""Run the Overleaf figure generator unchanged, archive inputs, and compare its table.

Usage: conda run -n base python -u reproduce_paper.py
Outputs go to reproduction/; existing paper figures and local model edits are preserved.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import importlib.util
from pathlib import Path
import subprocess
import sys

import h5py
import matplotlib
matplotlib.use("Agg")
import numpy as np

ROOT = Path(__file__).resolve().parent


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-dir", type=Path,
                        default=ROOT / "paper" if (ROOT / "paper/make_cabmod_figures.py").exists() else ROOT,
                        help="Generator checkout; defaults to the local Overleaf clone or this repository")
    parser.add_argument("--ablate-dir", type=Path, default=ROOT.parent / "ablate")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--extend-down-to", type=float, help="Extend baseline speeds to this value in km/s")
    parser.add_argument("--extra-velocity", action="append", type=float, default=[], help="Additional entry speed in km/s")
    parser.add_argument("--max-time", type=float, help="Maximum integration time in seconds")
    args = parser.parse_args()
    extended = args.extend_down_to is not None or bool(args.extra_velocity)
    if args.extend_down_to is not None and not 0 < args.extend_down_to < 32:
        parser.error("--extend-down-to must be between 0 and 32 km/s")
    if any(not np.isfinite(v) or v <= 0 for v in args.extra_velocity):
        parser.error("Extra velocities must be finite and positive")
    if args.max_time is not None and (not np.isfinite(args.max_time) or args.max_time <= 0):
        parser.error("--max-time must be finite and positive")
    if args.output_dir is None:
        args.output_dir = ROOT / ("reproduction_extended" if extended else "reproduction")
    source = args.paper_dir / "make_cabmod_figures.py"
    reference_path = args.paper_dir / "figures/velocity_shift_table.tex"
    if not reference_path.exists():
        reference_path = ROOT / "reference/velocity_shift_table.tex"
    if not source.exists() or not reference_path.exists():
        parser.error("The figure generator and reference/velocity_shift_table.tex are required")
    sys.path.insert(0, str(args.ablate_dir / "src"))
    spec = importlib.util.spec_from_file_location("paper_generator", source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if extended:
        from extended_paper_plots import make_profiles
        additions = list(args.extra_velocity)
        if args.extend_down_to is not None:
            additions.append(args.extend_down_to)
            if args.extend_down_to < 20:
                additions.append(20.)
        module.FIGURE1_VELOCITIES_KM_S = np.unique(np.r_[module.FIGURE1_VELOCITIES_KM_S, additions])
        module.FIGURE2_BASELINE_VELOCITIES_KM_S = np.unique(np.r_[module.FIGURE2_BASELINE_VELOCITIES_KM_S, additions])
        module.make_figure1 = lambda: make_profiles(module)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    module.FIG_DIR = args.output_dir / "figures"
    module.VELOCITY_SHIFT_TABLE_PATH = module.FIG_DIR / "velocity_shift_table.tex"
    cache = {}
    captured_raw = {}
    rows = []

    with h5py.File(args.output_dir / "paper_results.h5", "w") as archive:
        archive.attrs.update({
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "paper_commit": ("2f4de0df4b3d7c0b096a9e91db112603f22c7141"
                             if args.paper_dir.resolve() == ROOT.resolve()
                             else git(args.paper_dir, "rev-parse", "HEAD")),
            "generator_repository_commit": git(args.paper_dir, "rev-parse", "HEAD"),
            "ablate_commit": git(args.ablate_dir, "rev-parse", "HEAD"),
            "ablate_status": git(args.ablate_dir, "status", "--short"),
            "generator_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "python_version": sys.version,
            "time_utc": str(module.DEFAULT_TIME),
            "latitude_deg": module.DEFAULT_LAT,
            "longitude_deg": module.DEFAULT_LON,
            "initial_mass_kg": module.DEFAULT_MASS_KG,
            "material": module.DEFAULT_MATERIAL,
            "angle_convention": "Elevation above horizon; passed as zenith_ang in metablate",
            "peak_definition": "argmax(abs(numpy.gradient(mass, time, edge_order=1)))",
            "extended_velocity_range": extended,
        })
        archive.create_dataset("profile_entry_velocities_km_s", data=module.FIGURE1_VELOCITIES_KM_S)
        archive.create_dataset("comparison_baseline_velocities_km_s", data=module.FIGURE2_BASELINE_VELOCITIES_KM_S)
        for package in ("numpy", "scipy", "matplotlib", "h5py", "pymsis", "xarray"):
            archive.attrs[f"version_{package}"] = importlib.metadata.version(package)
        archive.create_dataset("sources/make_cabmod_figures.py", data=source.read_text())
        archive.create_dataset("sources/reproduce_paper.py", data=Path(__file__).read_text())
        if extended:
            archive.create_dataset("sources/extended_paper_plots.py", data=(ROOT / "extended_paper_plots.py").read_text())
        for path in sorted((args.ablate_dir / "src").rglob("*.py")):
            archive.create_dataset("sources/ablate/" + str(path.relative_to(args.ablate_dir / "src")),
                                   data=path.read_text())
        archive.create_dataset("sources/ablate/pyproject.toml",
                               data=(args.ablate_dir / "pyproject.toml").read_text())
        archive.create_dataset("reference/velocity_shift_table.tex",
                               data=reference_path.read_text())

        original_build = module.build_kero_model
        original_simulate = module.simulate_case
        original_write = module.write_velocity_shift_table

        def build(*a, **kw):
            model = original_build(*a, **kw)
            if args.max_time is not None or extended:
                model.config.set("integrate", "max_time_sec", str(args.max_time or 30.))
            if "atmosphere" not in archive:
                profile = model.atmosphere._profile
                atmosphere = archive.create_group("atmosphere")
                atmosphere.attrs["density_scale"] = 1.0
                atmosphere.attrs["MSIS_version"] = "2.1"
                atmosphere.create_dataset("altitude_m", data=profile.alt.values)
                for name in profile.data_vars:
                    atmosphere.create_dataset(name, data=profile[name].values.reshape(-1))
                config = archive.create_group("model_config")
                for section in model.config.sections():
                    for key, value in model.config.items(section):
                        config.attrs[f"{section}.{key}"] = value
                for key, value in module.metablate.material.get(module.DEFAULT_MATERIAL).items():
                    archive.require_group("material").attrs[key] = value
            original_run = model.run
            original_integrate = model.integrate

            def integrate(*a, **kw):
                result = original_integrate(*a, **kw)
                if not result.success:
                    raise RuntimeError(f"Integration failed: {result.message}")
                captured_raw["solver_status"] = result.status
                captured_raw["solver_message"] = result.message
                captured_raw["solver_nfev"] = result.nfev
                return result

            def run(*a, **kw):
                result = original_run(*a, **kw)
                captured_raw["result"] = result
                return result

            model.integrate = integrate
            model.run = run
            return model

        def simulate(velocity_km_s, density_scale=1.0,
                     entry_elevation_angle_deg=module.DEFAULT_ENTRY_ELEVATION_ANGLE_DEG):
            key = tuple(map(float, (velocity_km_s, density_scale, entry_elevation_angle_deg)))
            if key in cache:
                return cache[key]
            print(f"Simulating v={key[0]:.4f} km/s, gamma={key[1]:g}, elevation={key[2]:g} deg", flush=True)
            captured_raw.clear()
            result = original_simulate(*key)
            raw = captured_raw.pop("result")
            if not all(np.all(np.isfinite(raw[name])) for name in raw.data_vars):
                raise RuntimeError(f"Nonfinite trajectory: {key}")
            if not np.all(np.diff(raw.t.values) > 0) or np.any(raw.mass.values <= 0):
                raise RuntimeError(f"Invalid time or mass trajectory: {key}")
            peak = int(np.argmax(np.abs(np.gradient(raw.mass.values, raw.t.values))))
            if peak in (0, len(raw.t) - 1):
                raise RuntimeError(f"Peak at integration boundary: {key}")
            if not np.isclose(raw.altitude.values[peak] / 1000, result["peak_altitude_km"]):
                raise RuntimeError(f"Peak mismatch: {key}")
            group = archive.create_group(f"trajectories/case_{len(cache):03d}")
            group.attrs.update(dict(zip(("entry_velocity_km_s", "density_scale", "elevation_deg"), key)))
            group.attrs.update(captured_raw)
            group.attrs["peak_altitude_km"] = result["peak_altitude_km"]
            group.attrs["peak_index_time_order"] = peak
            group.create_dataset("time_s", data=raw.t.values)
            for name in raw.data_vars:
                group.create_dataset(name, data=raw[name].values, compression="gzip")
            for name, value in result.items():
                group.create_dataset("plot_data/" + name, data=value)
            archive.flush()
            cache[key] = result
            print(f"  Peak: {result['peak_altitude_km']:.6f} km ({len(raw.t)} samples)", flush=True)
            return result

        def write(table_rows):
            rows.extend(table_rows)
            original_write(table_rows)

        module.build_kero_model = build
        module.simulate_case = simulate
        module.write_velocity_shift_table = write
        module.main()
        for name in rows[0]:
            archive.create_dataset("velocity_shift_table/" + name, data=[row[name] for row in rows])
        if extended:
            archive.attrs["unique_trajectory_count"] = len(cache)
            archive.attrs["reference_comparison"] = "Not applicable: velocity family extended beyond the paper"
            print(f"Archived {len(cache)} extended trajectories: {archive.filename}", flush=True)
            return
        reference = reference_path.read_text()
        generated = module.VELOCITY_SHIFT_TABLE_PATH.read_text()
        reference_rows = [line.strip() for line in reference.splitlines() if line.startswith(("1.2 &", "0.8 &"))]
        generated_rows = [line.strip() for line in generated.splitlines() if line.startswith(("1.2 &", "0.8 &"))]
        matched = reference_rows == generated_rows
        archive.attrs["all_printed_table_rows_match"] = matched
        archive.attrs["unique_trajectory_count"] = len(cache)
        archive.attrs["matching_printed_table_rows"] = sum(a == b for a, b in zip(reference_rows, generated_rows))
        archive.attrs["printed_table_row_count"] = len(reference_rows)
        archive.create_dataset("comparison/reference_rows", data=reference_rows)
        archive.create_dataset("comparison/generated_rows", data=generated_rows)
        print(f"All printed table rows match the paper: {matched}", flush=True)
        for gamma in (1.2, 0.8):
            family = [row for row in rows if row["gamma"] == gamma]
            print(f"gamma={gamma}: mean inferred gamma={np.mean([r['inferred_gamma'] for r in family]):.8f}; "
                  f"mean error={np.mean([r['gamma_error_percent'] for r in family]):+.6f}%", flush=True)
        if not matched:
            for old, new in zip(reference_rows, generated_rows):
                if old != new:
                    print(f"Reference: {old}\nGenerated: {new}", flush=True)
        print(f"Archived {len(cache)} trajectories: {archive.filename}", flush=True)


if __name__ == "__main__":
    main()
