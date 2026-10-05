"""Compare the standalone function with article Figures 3 and 4."""
from pathlib import Path
import h5py
import matplotlib.pyplot as plt
import numpy as np
from dimant_oppenheim import electron_density

out = Path(__file__).parent / "figures" / "dimant_oppenheim"
reference = Path(__file__).parent / "reference" / "dimant_oppenheim"
R, theta = np.linspace(.01, 5, 160), np.linspace(0, np.pi, 9)
profiles = np.array([[electron_density(x * np.cos(t), x * np.sin(t)) for x in R] for t in theta])
with h5py.File(out / "profiles.h5", "w") as f:
    f["R_over_lambda_T"], f["theta_radians"], f["ne_over_n_star"] = R, theta, profiles
fig, ax = plt.subplots(figsize=(7.2, 6))
for i, row in enumerate(profiles):
    ax.semilogy(R, np.pi * row, "r--" if i in (0, 8) else "k-", linewidth=1)
# Figure 3 caption and Eq. 17: M with q -> lambda_T/R equals pi*ne/n_star.
ax.set(xlim=(0, 5), ylim=(.005, 1000), xlabel=r"$R/\lambda_T$", ylabel=r"$\pi\,n_e/n_*$ (Figure 3 normalization)", title="Standalone density: same angles as Figure 3")
fig.subplots_adjust(left=.15, bottom=.22, top=.90)
fig.text(.15, .08, "Scripts: dimant_oppenheim.py + compare_article.py", fontsize=11)
fig.savefig(out / "profiles.png", dpi=200)
plt.close(fig)

for number, computed in [(3, "profiles.png"), (4, "density.png")]:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, path, title in zip(axes, [reference / f"article_figure{number}.png", out / computed], [f"Article, Figure {number}", "Standalone program"]):
        ax.imshow(plt.imread(path))
        ax.set_title(title, fontsize=12)
        ax.axis("off")
    fig.subplots_adjust(left=.02, right=.98, bottom=.10, top=.86, wspace=.08)
    if number == 4:
        fig.text(.5, .025, "Figure 4: our chosen display scale is 8 pi times n_e/n_star; the article does not specify its relative-unit scale.", ha="center", fontsize=11)
    fig.savefig(out / f"comparison_figure{number}.png", dpi=160)
    plt.close(fig)
