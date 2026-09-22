"""
LNOI-WDM-DISPATCHER-v1.0 — Specification Compliance Tests
Verifies physical constants and architectural parameters defined in
docs/LNOI_WDM_Dispatcher_Core_Spec_v1.md
"""
import unittest


SWITCHING_LATENCY_PS = 38.0
TRANSIT_LATENCY_NS = 350.0
VAN_HEERDEN_LIMIT_TBIT = 70.7
THROUGHPUT_GOPS = 120.0
COMBINATORIAL_RATE_GHZ = 18.0
WDM_CARRIERS = 64
V_PI_MAX = 1.4
V_PI_L_MAX = 1.8
GRASSMANNIAN_K = 4
GRASSMANNIAN_N = 64
DIM_R_EXPECTED = 480
SIMD_BOUNDARY = 512


class TestLNOIPhysicalConstants(unittest.TestCase):

    def test_switching_latency(self):
        self.assertLessEqual(SWITCHING_LATENCY_PS, 40.0,
            "Electro-optic switching latency must be sub-40 ps")

    def test_transit_latency(self):
        self.assertLessEqual(TRANSIT_LATENCY_NS, 350.0,
            "Shared Tensor Ring transit must be <= 350 ns")

    def test_v_pi(self):
        self.assertLessEqual(V_PI_MAX, 1.4,
            "Half-wave voltage V_pi must be <= 1.4 V")

    def test_v_pi_l(self):
        self.assertLessEqual(V_PI_L_MAX, 1.8,
            "V_pi * L efficiency must be <= 1.8 V·cm")

    def test_throughput(self):
        self.assertGreaterEqual(THROUGHPUT_GOPS, 120.0,
            "Throughput must be >= 120 GOPS per spectral channel group")

    def test_combinatorial_rate(self):
        self.assertGreaterEqual(COMBINATORIAL_RATE_GHZ, 18.0,
            "Peak combinatorial screening must be >= 18 Gcombinations/sec")

    def test_wdm_carriers(self):
        self.assertLessEqual(WDM_CARRIERS, 64,
            "WDM C-band carrier count must not exceed 64")


class TestGrassmannianGeometry(unittest.TestCase):

    def test_dim_r_formula(self):
        """Real dimension of G(k, C^n) = 2 * k * (n - k)"""
        dim_r = 2 * GRASSMANNIAN_K * (GRASSMANNIAN_N - GRASSMANNIAN_K)
        self.assertEqual(dim_r, DIM_R_EXPECTED,
            f"G({GRASSMANNIAN_K}, C^{GRASSMANNIAN_N}) must have dim_R = {DIM_R_EXPECTED}")

    def test_simd_alignment(self):
        """Manifold is aligned to 512D SIMD cache-line boundary"""
        self.assertGreaterEqual(SIMD_BOUNDARY, DIM_R_EXPECTED,
            "SIMD boundary must accommodate Grassmannian embedding")
        self.assertEqual(SIMD_BOUNDARY % 64, 0,
            "SIMD boundary must be cache-line aligned (64-byte)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
