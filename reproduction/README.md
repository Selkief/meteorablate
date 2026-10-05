# Reproduction of the neutral-density / meteor-head-echo paper

Run date: 2026-10-01. The paper's headline numerical results are reproduced
at their published precision. Individual table rows do not all match exactly.

## Run

From the sabmod repository root:

```bash
conda run --no-capture-output -n base python -u reproduce_paper.py
conda run --no-capture-output -n base python -u check_paper_numerics.py
```

The first command reads the original generator in `paper/`, redirects its
outputs here, checks solver completion and trajectory validity, and compares
the generated table with the Overleaf table. It caches repeated identical
cases, without changing the equations, parameters, solver settings, peak
definition, interpolation, or figure layout. Running it replaces this run's
HDF5 file and reproduced figure files.

The second command changes only the maximum integration step in three
diagnostic simulations. Its results go to a separate HDF5 file.

The required `ablate` source checkout is the sibling directory `../ablate`.
`reproduce_paper.py --ablate-dir PATH` and `--paper-dir PATH` can override
locations. The numerical-check script also accepts `--ablate-dir PATH`.

## Source versions

| Source | Revision |
| --- | --- |
| Overleaf project `69f34677fe6aee3c6c1307c2` | `2f4de0df4b3d7c0b096a9e91db112603f22c7141` |
| `jvierine/sabmod`, fetched `origin/main` | `995729dd32c0b5f80193c87e1ee35120ff970d40` |
| Local `danielk333/ablate` checkout | `c2c8b34a5b5986f3f1a59363786e3b162ddde1e5` |

The GitHub and Overleaf figure generators are byte-identical, SHA256
`bf7a34e69bebb037444fe55f0b665eb95e8136011e69cfcf37be21a5389d8808`.
The local `ablate` checkout has a modified `version.py` that lets it import
from source without installed package metadata. The archive records that
modification and copies every Python source file used from its source tree.
Untracked example scripts are outside that tree and are not used.

The existing sabmod working tree is on an older revision and has local edits.
Those scripts differ substantially from the model in this paper; they were
not used for this reproduction. The latest GitHub README correctly identifies
the paper generator and its `metablate` dependency.

Environment: Python 3.13.1; NumPy 2.1.3; SciPy 1.17.1;
Matplotlib 3.10.0; h5py 3.14.0; pymsis 0.11.0.
The HDF5 metadata also records xarray's version.

## Inputs and outputs

The model is `metablate.KeroSzasz2008`, with cometary material:
initial mass 1e-8 kg, bulk density 1000 kg/m3, vapor molecular mass 20 amu,
specific heat 1200 J/(kg K), latent heat 6e6 J/kg, emissivity 0.9,
initial temperature 290 K, and fixed drag and heat-transfer coefficients of 1.
Sputtering is disabled. The initial altitude is 130 km.

MSIS 2.1 is evaluated at 69.30 N, 16.04 E,
2018-06-28 12:45:33 UTC. The paper generator caches a profile on a
50-150 km grid with 100 m spacing, interpolates it along the trajectory,
and scales density while leaving atmospheric temperature unchanged.
It uses library-default space-weather inputs. The actual evaluated
unscaled atmosphere, including all species and temperature, is archived.

The entry angles 70, 45, and 20 degrees are elevations above the horizon.
Despite its name, the model's `zenith_ang` parameter is passed to an
azimuth/elevation coordinate conversion, as the generator comments explain.

Figure 1 uses entry speeds 32, 53, and 72 km/s. The velocity-shift comparison
uses baseline speeds 32, 52, and 72 km/s, density factors 1.2 and 0.8,
and trial velocities scaled by gamma^(-1/3). A gamma=1 control is also generated.
There are 30 distinct simulated cases, all terminating successfully at the
model's minimum-mass event, with finite trajectories and interior peaks.

- `figures/meteor_ablation_single_column.pdf`: four-panel profiles.
- `figures/peak_ablation_height-1.20.pdf`: 20% density increase.
- `figures/peak_ablation_height-0.80.pdf`: 20% density decrease.
- `figures/peak_ablation_height-1.00.pdf`: unscaled control.
- `figures/velocity_shift_table.tex`: regenerated table.
- `figures/figure_captions.tex`: figure captions with generating-script
  provenance shown by default; `\showscriptprovenancefalse` hides it.
- `paper_results.h5`: raw trajectories in time order, plotting arrays,
  solver statuses, full-precision table, comparison rows, atmosphere,
  material parameters, model configuration, source snapshots, and versions.
- `numerical_checks.h5`: three half-step diagnostic trajectories and peaks.
- `figures/*.png`: renderings of the generated PDFs, inspected against the
  Overleaf figures.

The archive preserves the run's atmosphere and source inputs; the default
rerun still evaluates MSIS through the current library and its space-weather
cache. Later library or input changes can therefore change the results.

## Agreement with the paper

| Density factor | Mean inferred factor | Mean relative error | Published rounded values |
| --- | ---: | ---: | --- |
| 1.2 | 1.30877526 | +9.064605% | 1.31; +9% |
| 0.8 | 0.71664257 | -10.419679% | 0.72; -10% |

All 18 printed baseline peak heights and simple-scaling predictions match.
Ten of the 18 complete numerical rows match exactly; eight have differences
in the interpolated model velocity or derived quantities. The maximum
printed difference is 0.2 km/s in model velocity, 0.01 in inferred density
factor, and one percentage point in relative error. Both mean rows match.
The PDFs were rendered and visually compared with the paper's figures;
the profiles and density-shift plots closely agree.

The historical dependency versions and full-precision table inputs are not
included in the paper checkout. The cause of the small individual-row
differences has not been established, so this is not an exact reproduction
of every table entry.

## Numerical sensitivity and manuscript issues

The original peak is the maximum of `abs(numpy.gradient(mass, time))` on
RK45's adaptive output samples. The inverse height-to-velocity mapping uses
only three samples and linear interpolation, with extrapolation at endpoints.
These definitions are preserved here.

Halving RK45's maximum step from 0.05 to 0.025 s, while retaining the default
tolerances, gives the following baseline checks at 45-degree elevation:

| Entry speed (km/s) | Original peak (km) | Half-step peak (km) | Difference (km) |
| ---: | ---: | ---: | ---: |
| 32 | 99.735294 | 99.383397 | -0.351897 |
| 52 | 107.256657 | 107.349390 | +0.092733 |
| 72 | 112.512125 | 112.273167 | -0.238958 |

These checks show sensitivity of the sampled peak; they do not establish
convergence of the full density-bias table. A convergence study with explicit
state-appropriate tolerances and better peak localization is needed before
assigning uncertainty to its fine numerical details.

Two issues in the cloned manuscript are recorded without altering its source:

- `cabmod_text.tex` has an empty `\includegraphics{figures/ }` path where
  `figures/peak_ablation_height-1.20.pdf` is expected. Its caption also calls
  the vertically stacked density cases left/right.
- Its paragraph describing velocity shifts as about 10% larger/smaller
  disagrees with the actual velocity-shift table, especially the claim of
  a smaller shift for gamma=0.8. The later paragraph's approximately +9%
  and -10% inferred-density biases agrees with the reproduced mean rows.

The identification of maximum mass loss with radar detection/scattering
height remains a modeling assumption; this run reproduces the ablation
calculation, not a radar-scattering or observational validation.

For a fresh GitHub clone, the runner uses the repository-root generator and
the table under `reference/`; the original private Overleaf manuscript is
not needed. Source snapshots inside the delivered HDF5 files describe the
original runs. The published wrapper additionally supports this layout.
