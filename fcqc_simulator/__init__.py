"""
Karabut-FCQC Physical Simulator Package.
Reproduces Karabut glow-discharge LENR phenomena and Fractional Charge Quantum Coherence (FCQC).
"""

__version__ = "1.0.0"

from .constants import (
    HG201_TARGET_KEV,
    D0_BOND_TARGET_PM,
    KAPPA_TARGET_PS,
    GAMMA_511_REFERENCE,
)
from .config import (
    SimulationConfig,
    D0ClusterConfig,
    Hg201Config,
    SpinTransferConfig,
    Gamma511Config,
)
from .hg201_transition import Hg201TransitionModel
from .d0_cluster import D0ClusterModel
from .spin_transfer import SpinTransferModel
from .gamma_emission import GammaEmissionModel
from .non_hermitian_hamiltonian import NonHermitianSolver
from .hagelstein_coupling import HagelsteinCouplingModel
from .solver import FCQCSimulator

__all__ = [
    "FCQCSimulator",
    "SimulationConfig",
    "D0ClusterConfig",
    "Hg201Config",
    "SpinTransferConfig",
    "Gamma511Config",
    "Hg201TransitionModel",
    "D0ClusterModel",
    "SpinTransferModel",
    "GammaEmissionModel",
    "NonHermitianSolver",
    "HagelsteinCouplingModel",
]
