"""
Non-Hermitian Hamiltonian engine for dissipative open quantum systems
and coherent Hagelstein-Chaudhuri energy transfer dynamics.
"""

import numpy as np
from typing import Tuple, List, Optional


class NonHermitianSolver:
    """
    Solves Schrödinger-type or Lindblad-type dissipative dynamics under an effective
    non-Hermitian Hamiltonian H_eff = H_0 - (i/2) * sum_k (gamma_k * L_k^dagger * L_k).
    """

    def __init__(self, h_hermitian: np.ndarray, jump_operators: Optional[List[Tuple[float, np.ndarray]]] = None):
        """
        Args:
            h_hermitian: Hermitian part of Hamiltonian (N x N)
            jump_operators: List of tuples (rate_gamma, operator_L)
        """
        self.h0 = np.array(h_hermitian, dtype=np.complex128)
        self.dim = self.h0.shape[0]
        self.jump_ops = jump_operators or []
        self.h_eff = self._build_effective_hamiltonian()

    def _build_effective_hamiltonian(self) -> np.ndarray:
        h_eff = self.h0.copy()
        for gamma, l_op in self.jump_ops:
            l_mat = np.array(l_op, dtype=np.complex128)
            l_dag_l = np.conjugate(l_mat.T) @ l_mat
            h_eff -= 0.5j * gamma * l_dag_l
        return h_eff

    def propagate_state(self, psi0: np.ndarray, dt: float, steps: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Propagate pure state psi(t) under H_eff using 4th-order Runge-Kutta.
        Returns:
            times: 1D array of time points
            states: (steps+1, dim) array of normalized state vectors
        """
        psi = np.array(psi0, dtype=np.complex128)
        psi = psi / np.linalg.norm(psi)
        
        times = np.linspace(0, dt * steps, steps + 1)
        states = np.zeros((steps + 1, self.dim), dtype=np.complex128)
        states[0] = psi

        def dpsi_dt(state: np.ndarray) -> np.ndarray:
            # i * dpsi/dt = H_eff * psi  =>  dpsi/dt = -i * H_eff * psi
            return -1.0j * (self.h_eff @ state)

        for step in range(steps):
            k1 = dpsi_dt(psi)
            k2 = dpsi_dt(psi + 0.5 * dt * k1)
            k3 = dpsi_dt(psi + 0.5 * dt * k2)
            k4 = dpsi_dt(psi + dt * k3)
            psi = psi + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
            norm = np.linalg.norm(psi)
            if norm > 1e-15:
                states[step + 1] = psi / norm
            else:
                states[step + 1] = psi

        return times, states

    def calculate_eigenvalues(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute complex eigenvalues and eigenvectors of H_eff.
        Real parts correspond to energy levels, imaginary parts to decay widths.
        """
        evals, evecs = np.linalg.eig(self.h_eff)
        # Sort by real part
        idx = np.argsort(np.real(evals))
        return evals[idx], evecs[:, idx]
