# Extended entry-speed comparison

The model and atmosphere are those used for the paper reproduction. The
velocity families are extended to include 11, 15, and 20 km/s. The 15 km/s
point was selected for the requested additional speed.

```bash
conda run --no-capture-output -n base python -u reproduce_paper.py --extend-down-to 11 --extra-velocity 15
```

The profiles use 11, 15, 20, 32, 53, and 72 km/s. The peak-height comparison
uses baseline speeds 11, 15, 20, 32, 52, and 72 km/s. As in the paper, trials
in the scaled atmosphere use those speeds times gamma^(-1/3). Consequently,
the lowest trial speed for gamma=1.2 is approximately 10.35 km/s.

Entry elevation angles remain 70, 45, and 20 degrees above the horizon;
density factors remain 1.2, 1.0, and 0.8. Cometary material, initial mass,
MSIS inputs, model equations, integrator settings, and the sampled-gradient
peak definition remain as documented in `../reproduction/README.md`.

The maximum integration duration is extended from 5 to 30 seconds to allow
the low-speed trajectories to reach their mass-loss peaks. In the initial
11 km/s, 20-degree baseline check, the peak occurs at about 10 seconds and
92.45 km. Low-speed particles may retain mass at the end of the integration;
the original minimum-mass stopping event remains enabled.

Outputs:

- `figures/meteor_ablation_single_column.pdf`: six-speed profiles.
- `figures/peak_ablation_height-1.20.pdf`: density increase.
- `figures/peak_ablation_height-0.80.pdf`: density decrease.
- `figures/peak_ablation_height-1.00.pdf`: control.
- `figures/velocity_shift_table.tex`: expanded table using the expanded
  piecewise-linear mapping, so its interpolation differs from the paper's
  original three-speed calculation.
- `paper_results.h5`: raw trajectories, derived plotting arrays, exact
  speed families, atmosphere, model configuration, solver statuses,
  full-precision table, dependency versions, and source snapshots.
- `figures/figure_captions.tex`: captions with a script-provenance toggle,
  shown by default.

The original paper-range reproduction remains in `../reproduction/`.

The completed run contains 57 distinct trajectories. All solvers completed
successfully and every sampled mass-loss peak lies inside its trajectory.
Thirty-nine cases stop at the minimum-mass event; eighteen reach the
30-second duration with mass remaining. Peak times range from 0.29 to
10.55 seconds. All four PDFs were rendered and visually inspected.
