"""
Karabut-FCQC Physical Simulator Package.
Reproduces Karabut glow-discharge LENR phenomena and Fractional Charge Quantum Coherence (FCQC).
"""

__version__ = "1.0.0"

from .config import (
    D0ClusterConfig,
    Gamma511Config,
    Hg201Config,
    SimulationConfig,
    SpinTransferConfig,
)
from .constants import (
    D0_BOND_TARGET_PM,
    GAMMA_511_REFERENCE,
    HG201_TARGET_KEV,
    KAPPA_TARGET_PS,
)
from .d0_cluster import D0ClusterModel
from .gamma_emission import GammaEmissionModel
from .hagelstein_coupling import HagelsteinCouplingModel
from .hg201_transition import Hg201TransitionModel
from .non_hermitian_hamiltonian import NonHermitianSolver
from .solver import FCQCSimulator
from .spin_transfer import SpinTransferModel

__all__ = [
    "D0_BOND_TARGET_PM",
    "GAMMA_511_REFERENCE",
    "HG201_TARGET_KEV",
    "KAPPA_TARGET_PS",
    "D0ClusterConfig",
    "D0ClusterModel",
    "FCQCSimulator",
    "Gamma511Config",
    "GammaEmissionModel",
    "HagelsteinCouplingModel",
    "Hg201Config",
    "Hg201TransitionModel",
    "NonHermitianSolver",
    "SimulationConfig",
    "SpinTransferConfig",
    "SpinTransferModel",
]

