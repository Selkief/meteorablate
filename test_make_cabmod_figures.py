"""Fast contract tests; the no-argument generator is the full integration test."""
import unittest
from unittest.mock import patch
import numpy as np
import make_cabmod_figures as figures


class FigureDefaultsTest(unittest.TestCase):
    def test_speed_families_match_reference(self):
        np.testing.assert_array_equal(figures.FIGURE1_VELOCITIES_KM_S,
                                      [11, 15, 20, 32, 53, 72])
        np.testing.assert_array_equal(figures.FIGURE2_BASELINE_VELOCITIES_KM_S,
                                      [11, 15, 20, 32, 52, 72])

    def test_default_generates_every_figure(self):
        with patch.object(figures, "make_figure1") as profiles, \
             patch.object(figures, "make_figure2", return_value=[]) as density, \
             patch.object(figures, "write_velocity_shift_table"), \
             patch.object(figures, "write_trajectory_archive"):
            figures.main()
        profiles.assert_called_once_with()
        self.assertEqual([call.kwargs["gamma"] for call in density.call_args_list],
                         [1.2, 1.0, .8])

    def test_latest_api_and_low_speed_duration(self):
        model = figures.build_kero_model()
        self.assertIsInstance(model, figures.KeroSzasz2008)
        self.assertEqual(model.options.max_time, 30.)
        self.assertEqual(model.options.start_altitude, 130000.)


if __name__ == "__main__":
    unittest.main()
