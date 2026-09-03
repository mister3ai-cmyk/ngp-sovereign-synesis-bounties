# Copyright 2026 Synapse Core Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sovereign_materials_optimizer_v3 import SovereignMaterialsOptimizer


class TestSovereignMaterialsOptimizer(unittest.TestCase):

    def setUp(self):
        self.optimizer = SovereignMaterialsOptimizer()

    # ------------------------------------------------------------------
    # Basic API contract
    # ------------------------------------------------------------------
    def test_optimization_returns_success(self):
        result = self.optimizer.optimize_alloy(carbon_x=1.25, temperature_k=300.0)
        self.assertEqual(result["status"], "SUCCESS")

    def test_required_keys_present(self):
        result = self.optimizer.optimize_alloy(carbon_x=1.0, temperature_k=300.0)
        expected_keys = {
            "status",
            "formation_energy_ev_atom",
            "saturation_induction_tesla",
            "is_metastable_stable",
            "optimal_dvs_volume_factor",
            "local_magnetic_moments_mu_b",
            "free_energy_components",
        }
        self.assertTrue(expected_keys.issubset(result.keys()))

    # ------------------------------------------------------------------
    # Carbon-fraction sweep
    # ------------------------------------------------------------------
    def test_optimization_carbon_ranges(self):
        for x in [0.0, 0.5, 1.0, 1.5, 2.0]:
            with self.subTest(carbon_x=x):
                result = self.optimizer.optimize_alloy(carbon_x=x, temperature_k=300.0)
                self.assertEqual(result["status"], "SUCCESS")
                self.assertIsInstance(result["formation_energy_ev_atom"], float)
                self.assertIsInstance(result["saturation_induction_tesla"], float)

    # ------------------------------------------------------------------
    # Physical sanity checks
    # ------------------------------------------------------------------
    def test_volume_factor_in_bounds(self):
        result = self.optimizer.optimize_alloy(carbon_x=1.0, temperature_k=300.0)
        vf = result["optimal_dvs_volume_factor"]
        self.assertGreaterEqual(vf, 0.85)
        self.assertLessEqual(vf, 1.40)

    def test_saturation_induction_positive(self):
        result = self.optimizer.optimize_alloy(carbon_x=1.0, temperature_k=300.0)
        self.assertGreater(result["saturation_induction_tesla"], 0.0)

    def test_magnetic_moments_reasonable(self):
        result = self.optimizer.optimize_alloy(carbon_x=1.0, temperature_k=300.0)
        moments = result["local_magnetic_moments_mu_b"]
        for site, mu in moments.items():
            self.assertGreater(mu, 0.0, f"Moment at {site} should be positive")
            self.assertLess(mu, 4.0,    f"Moment at {site} should be < 4 mu_B")

    # ------------------------------------------------------------------
    # Temperature boundary
    # ------------------------------------------------------------------
    def test_zero_temperature(self):
        result = self.optimizer.optimize_alloy(carbon_x=1.0, temperature_k=0.0)
        self.assertEqual(result["status"], "SUCCESS")
        self.assertAlmostEqual(result["free_energy_components"]["f_vib_ev"], 0.0, places=5)

    # ------------------------------------------------------------------
    # LiNbO3 holographic density (Van Heerden limit)
    # ------------------------------------------------------------------
    def test_linbo3_density_estimation(self):
        density = self.optimizer.estimate_linbo3_density()
        self.assertAlmostEqual(density, 70.7, places=1)

    # ------------------------------------------------------------------
    # Birch-Murnaghan EOS at reference points
    # ------------------------------------------------------------------
    def test_bm_energy_at_equilibrium(self):
        E0, V0, B0, B0p = self.optimizer.get_birch_murnaghan_params(0.0)
        E_at_V0 = self.optimizer.calculate_bm_energy(V0, E0, V0, B0, B0p)
        self.assertAlmostEqual(E_at_V0, E0, places=6)


if __name__ == "__main__":
    unittest.main()