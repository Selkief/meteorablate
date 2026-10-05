"""Run with: conda run -n base python plot_dimant_oppenheim.py"""
from pathlib import Path
import h5py
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, ListedColormap
import numpy as np
from dimant_oppenheim import electron_density

SHOW_PROVENANCE = True
PLOT_SCALE = 8 * np.pi  # Chosen relative-unit scale; Figure 4 does not specify it.
out = Path(__file__).parent / "figures" / "dimant_oppenheim"
out.mkdir(parents=True, exist_ok=True)
z, r = np.linspace(-5, 20, 101), np.linspace(-10, 10, 81)
ne = np.array([[electron_density(x, y) for x in z] for y in r])
Z, Y = np.meshgrid(z, r)
ne[np.hypot(Z, Y) > 20] = np.nan  # Same outer boundary as article Figure 4.
with h5py.File(out / "density.h5", "w") as f:
    f["z_over_lambda_T"], f["r_over_lambda_T"], f["ne_over_n_star"] = z, r, ne
    f.attrs["script"] = "plot_dimant_oppenheim.py; dimant_oppenheim.py"
    f.attrs["display_scale"] = PLOT_SCALE
    f.attrs["normalization"] = "ne/n_star; n_star=8*pi*r_M^2*n0*nA*(1+m/mA)*Gion/(sqrt(3)*lambda_T)"

plt.rcParams.update({"font.size": 11})
fig, ax = plt.subplots(figsize=(7.2, 6))
# Read the original colorbar so both figures use the article's actual colors.
reference = plt.imread(Path(__file__).parent / "reference" / "dimant_oppenheim" / "article_figure4.png")
cmap = ListedColormap(reference[143:1297, 2040, :3][::-1])
im = ax.pcolormesh(z, r, PLOT_SCALE * ne, cmap=cmap, norm=LogNorm(1e-3, 1e4), shading="auto", rasterized=True)
fig.colorbar(im, ax=ax, label=r"$8\pi\,n_e/n_*$ (relative units)")
ax.plot(0, 0, "wo", markersize=4)
ax.axhline(0, color="skyblue", linestyle="--", linewidth=1)
ax.set(xlabel=r"$z/\lambda_T$ (positive behind meteor)", ylabel=r"$r/\lambda_T$", title="Standalone Dimant-Oppenheim density", aspect="equal")
fig.subplots_adjust(left=.12, right=.90, bottom=.21, top=.90)
if SHOW_PROVENANCE:
    fig.text(.12, .08, "Scripts: dimant_oppenheim.py + plot_dimant_oppenheim.py", fontsize=11)
fig.savefig(out / "density.png", dpi=200)
fig.savefig(out / "density.pdf", dpi=200)
plt.close(fig)
