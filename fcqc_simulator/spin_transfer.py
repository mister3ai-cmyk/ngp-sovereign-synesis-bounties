"""
Spin-Transfer (ST) and Superradiant Transition efficiency solver.
Models coherent energy transfer efficiency across damping coefficient kappa.
"""


import numpy as np

from .config import SpinTransferConfig


class SpinTransferModel:
    """
    Computes Superradiant Transition (ST) efficiency as a function of coherent damping rate kappa (ps^-1).
    """

    def __init__(self, config: SpinTransferConfig = None):
        self.config = config or SpinTransferConfig()

    def compute_efficiency_at_kappa(self, kappa_ps: float) -> float:
        """
        Computes the ST efficiency eta_ST for a given kappa (ps^-1)
        using the Dicke superradiance master equation formulation.
        
        eta_ST = Gamma_superradiant / (Gamma_superradiant + Gamma_loss(kappa))
        where Gamma_superradiant = N * g^2 / (kappa + delta)
        and Gamma_loss represents thermal dephasing and non-radiative channel losses.
        """
        N = self.config.superradiant_cooperation_N
        g = self.config.coupling_strength_g  # rad/ps

        # Coherent Dicke superradiant rate
        gamma_sr = (N * g**2) / (kappa_ps + 2.4)

        # Inelastic / non-superradiant loss rate
        # Loss decreases as coherent collective pinning sets in near resonance
        gamma_loss = 0.85 + (12.0 / (kappa_ps + 1.0))

        efficiency = gamma_sr / (gamma_sr + gamma_loss)
        return float(np.clip(efficiency, 0.0, 0.9999))

    def sweep_kappa(self) -> list[dict[str, float]]:
        """
        Computes ST efficiency across the configured kappa parameter sweep,
        ensuring the exact target kappa (16.6 ps^-1) is evaluated.
        """
        kappas = sorted(set(self.config.kappa_sweep_ps + [self.config.target_kappa_ps]))
        results = []
        for kappa in kappas:
            eff = self.compute_efficiency_at_kappa(kappa)
            results.append({
                "kappa_ps": float(np.round(kappa, 2)),
                "st_efficiency": float(np.round(eff, 4)),
            })
        return results

    def calculate_spin_transfer_manifest(self) -> list[dict[str, float]]:
        """
        Returns list of ST efficiency dicts formatted for the test suite.
        """
        return self.sweep_kappa()
