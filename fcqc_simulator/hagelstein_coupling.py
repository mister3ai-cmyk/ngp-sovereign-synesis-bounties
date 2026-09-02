"""
Phonon-nuclear Hagelstein-Chaudhuri coupling model.
Simulates coherent multi-quanta vibrational excitation transfer to nuclear transitions.
"""

import numpy as np
from typing import Dict, Any, Tuple


class HagelsteinCouplingModel:
    """
    Models resonant energy fractionation and coherent phonon-nuclear excitation
    transfer under the Hagelstein-Chaudhuri non-perturbative lattice Hamiltonian.
    """

    def __init__(self, n_phonons: int = 10, coupling_g: float = 24.5):
        """
        Args:
            n_phonons: Truncation limit for phonon Fock state space.
            coupling_g: Coupling parameter in rad/ps.
        """
        self.n_phonons = n_phonons
        self.g = coupling_g

    def construct_hamiltonian(self, delta_omega: float = 0.0) -> np.ndarray:
        """
        Builds the 2-level nuclear system coupled to N phonon modes:
        H = (omega_nuc / 2) * sigma_z + omega_ph * a_dag * a + g * (sigma_+ * a + sigma_- * a_dag)
        Returns:
            H_matrix of dimension (2 * n_phonons, 2 * n_phonons)
        """
        dim = 2 * self.n_phonons
        h_mat = np.zeros((dim, dim), dtype=np.complex128)

        # Basis indexing: |nuc, ph> where nuc in {0 (ground), 1 (excited)}, ph in {0..n_phonons-1}
        for ph in range(self.n_phonons):
            idx_g = ph  # |ground, ph>
            idx_e = self.n_phonons + ph  # |excited, ph>

            # Diagonal energies
            h_mat[idx_g, idx_g] = ph * 1.0  # Phonon energy
            h_mat[idx_e, idx_e] = delta_omega + ph * 1.0  # Nuclear detuning + phonon energy

            # Off-diagonal Jaynes-Cummings-like Hagelstein coupling
            if ph + 1 < self.n_phonons:
                idx_e_next = self.n_phonons + ph + 1
                # |g, ph+1> <-> |e, ph>
                coupling_element = self.g * np.sqrt(ph + 1)
                h_mat[ph + 1, idx_e] = coupling_element
                h_mat[idx_e, ph + 1] = coupling_element

        return h_mat
