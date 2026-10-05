"""Independent checks of the short density function against the article."""
import numpy as np
import pytest
from scipy.integrate import quad
from scipy.special import erf
from dimant_oppenheim import electron_density


@pytest.mark.parametrize("R", [.01, .1, 1., 5., 10.])
def test_axis_formulas(R):
    # Article Eqs. 43-44, independent of the general Eq. 48 quadrature.
    q = R ** (2 / 3)
    correction = (4 - np.pi) * np.sqrt(2 * np.pi) / (2 * np.sqrt(2 * np.pi + (4 - np.pi)**2 * q))
    ahead = (1 - correction) * np.exp(-1.5 * q) / R
    behind = (2 * np.sqrt(2 * np.pi / 3) / R * erf(np.sqrt(1.5 * q))
              - (correction + 1 + 4 / q) * np.exp(-1.5 * q)) / R
    assert electron_density(-R, 0) == pytest.approx(ahead, rel=1e-10)
    assert electron_density(R, 0) == pytest.approx(behind, rel=1e-10)


@pytest.mark.parametrize("R", [.1, 1., 5.])
def test_transverse_formula(R):
    # Transform xi=sin(phi): a smooth, independently evaluated integral.
    expected = quad(lambda p: np.sqrt(1 + 2 / np.pi * (R * np.sin(p))**(2 / 3))
                    * np.exp(-1.5 * (R * np.sin(p))**(2 / 3)) * np.sin(p),
                    0, np.pi / 2, epsabs=1e-11)[0] / R
    assert electron_density(0, R) == pytest.approx(expected, rel=1e-8)
