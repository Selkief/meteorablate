# Dimant-Oppenheim article figures

The reference PNGs are the embedded Figures 3 and 4, extracted without
alteration from the authors' version 2 PDF held by Boston University:

[Formation of plasma around a small meteoroid: 2. Implications for radar head echo](https://open.bu.edu/bitstreams/67a5df26-98ed-4fa5-af3a-a338397ceedd/download),
Y. S. Dimant and M. M. Oppenheim (2017), JGR Space Physics, 122, 4697-4711,
[doi:10.1002/2017JA023963](https://doi.org/10.1002/2017JA023963).

Figure 3 is on PDF page 19 and Figure 4 on PDF page 20 (including the
repository cover sheet). They remain the authors' figures and are included
here for comparison and attribution.

`plot_dimant_oppenheim.py` reads the Figure 4 colorbar column at image x=2040,
rows 143:1297, reversing it to map the printed 10^-3 through 10^4 ticks onto
the same colors. The numerical function does not depend on these images.

The article's Figure 3 normalization is `pi*ne/n_star`, from its caption
and Eq. 17. The Figure 4 relative-unit normalization is unspecified;
`8*pi*ne/n_star` is an explicitly chosen display scale, not a measured or
independently established physical electron density.
