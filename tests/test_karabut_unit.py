import sys
import os
import pathlib
import pytest

# Ensure root dir is in sys.path
root_dir = pathlib.Path(__file__).parent.parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from simulator import KarabutSimulator

def test_karabut_simulator_init():
    sim = KarabutSimulator(seed=123)
    assert sim.seed == 123
    assert sim.grid_points == 1000

def test_hg201_transition_range():
    sim = KarabutSimulator(seed=42)
    res = sim.calculate_hg201_transition()
    assert 1564.3 <= res["transition_keV"] <= 1565.3
    assert res["uncertainty_keV"] == 0.08

def test_d0_cluster_properties():
    sim = KarabutSimulator(seed=42)
    res = sim.simulate_d0_cluster()
    assert 2.25 <= res["bond_length_pm"] <= 2.35
    assert res["binding_energy_eV"] == 48.5

def test_spin_transfer_monotonicity():
    sim = KarabutSimulator(seed=42)
    res = sim.compute_spin_transfer()
    assert len(res) > 0
    k16 = [x for x in res if abs(x["kappa_ps"] - 16.6) < 0.1][0]
    assert k16["st_efficiency"] >= 0.92

def test_gamma_511_intensity_range():
    sim = KarabutSimulator(seed=42)
    res = sim.predict_gamma_511()
    assert abs(res["relative_intensity"] - 1.0) <= 0.15
