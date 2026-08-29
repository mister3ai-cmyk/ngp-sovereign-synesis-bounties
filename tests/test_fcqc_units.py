"""
Unit tests for fcqc_simulator components and physical models.
"""

import numpy as np
from fcqc_simulator.constants import (
    HG201_TARGET_KEV,
    HG201_TOLERANCE_KEV,
    D0_BOND_TARGET_PM,
    D0_BOND_TOLERANCE_PM,
    KAPPA_TARGET_PS,
    ST_EFFICIENCY_TARGET_MIN,
)
from fcqc_simulator.hg201_transition import Hg201TransitionModel
from fcqc_simulator.d0_cluster import D0ClusterModel
from fcqc_simulator.spin_transfer import SpinTransferModel
from fcqc_simulator.gamma_emission import GammaEmissionModel
from fcqc_simulator.non_hermitian_hamiltonian import NonHermitianSolver
from fcqc_simulator.hagelstein_coupling import HagelsteinCouplingModel
from fcqc_simulator.solver import FCQCSimulator


def test_hg201_transition_model():
    model = Hg201TransitionModel()
    res = model.calculate_transition_energy()
    assert res["within_tolerance"] is True
    assert abs(res["transition_keV"] - HG201_TARGET_KEV) <= HG201_TOLERANCE_KEV


def test_d0_cluster_model():
    model = D0ClusterModel()
    res = model.calculate_d0_manifest()
    assert res["within_tolerance"] is True
    assert abs(res["bond_length_pm"] - D0_BOND_TARGET_PM) <= D0_BOND_TOLERANCE_PM


def test_spin_transfer_model():
    model = SpinTransferModel()
    results = model.calculate_spin_transfer_manifest()
    target = min(results, key=lambda x: abs(x["kappa_ps"] - KAPPA_TARGET_PS))
    assert abs(target["kappa_ps"] - KAPPA_TARGET_PS) < 0.1
    assert target["st_efficiency"] >= ST_EFFICIENCY_TARGET_MIN


def test_gamma_emission_model():
    model = GammaEmissionModel()
    res = model.calculate_gamma_511_manifest()
    assert res["within_tolerance"] is True
    assert res["deviation_fraction"] <= 0.15


def test_non_hermitian_solver():
    h0 = np.array([[1.0, 0.5], [0.5, 2.0]], dtype=np.complex128)
    l_op = np.array([[0.0, 1.0], [0.0, 0.0]], dtype=np.complex128)
    solver = NonHermitianSolver(h0, jump_operators=[(0.1, l_op)])
    
    evals, _ = solver.calculate_eigenvalues()
    assert len(evals) == 2

    psi0 = np.array([1.0, 0.0], dtype=np.complex128)
    times, states = solver.propagate_state(psi0, dt=0.01, steps=10)
    assert len(times) == 11
    assert states.shape == (11, 2)


def test_hagelstein_coupling_model():
    model = HagelsteinCouplingModel(n_phonons=5, coupling_g=10.0)
    h_mat = model.construct_hamiltonian(delta_omega=0.0)
    assert h_mat.shape == (10, 10)


def test_fcqc_simulator_full_run():
    sim = FCQCSimulator()
    manifest = sim.run()
    assert "hg201" in manifest
    assert "d0_cluster" in manifest
    assert "spin_transfer" in manifest
    assert "gamma_511" in manifest
    assert manifest["arxiv_preprint_id"].startswith("2")
