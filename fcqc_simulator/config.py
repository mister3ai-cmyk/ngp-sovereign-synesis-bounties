"""
Configuration dataclasses and static presets for Karabut-FCQC simulation.
"""

from dataclasses import dataclass, field


@dataclass
class D0ClusterConfig:
    """Configuration for Deuterium(0) ultra-dense cluster calculations."""
    fractional_state_s: int = 2
    target_bond_length_pm: float = 2.30
    screening_factor: float = 1.842e12  # m^-1
    coulomb_cutoff_pm: float = 0.05
    spin_pairing_strength_eV: float = 345.2
    grid_points: int = 1000
    r_min_pm: float = 0.1
    r_max_pm: float = 10.0


@dataclass
class Hg201Config:
    """Configuration for Hg-201 nuclear up-conversion dynamics."""
    base_transition_energy_keV: float = 1564.8
    qed_vacuum_polarization_keV: float = -0.42
    qed_self_energy_keV: float = 0.68
    lattice_hyperfine_shift_keV: float = -0.26
    multipole_order: str = "M1/E2"
    nuclear_spin_ground: str = "3/2-"
    nuclear_spin_excited: str = "5/2-"


@dataclass
class SpinTransferConfig:
    """Configuration for Hagelstein-Chaudhuri phonon-nuclear coupling and ST-efficiency."""
    target_kappa_ps: float = 16.6
    kappa_sweep_ps: list[float] = field(default_factory=lambda: [5.0, 8.0, 10.0, 12.5, 15.0, 16.6, 20.0, 25.0, 30.0])
    coupling_strength_g: float = 24.5  # rad/ps
    superradiant_cooperation_N: int = 120
    cavity_detuning_GHz: float = 0.0
    time_span_ps: float = 50.0
    time_steps: int = 500


@dataclass
class Gamma511Config:
    """Configuration for 511 keV positron annihilation detection modeling."""
    positron_internal_pair_branching_ratio: float = 1.42e-4
    solid_angle_fraction: float = 0.048
    detector_efficiency_511: float = 0.65
    karabut_1995_norm_reference: float = 1.0


@dataclass
class SimulationConfig:
    """Global simulation master configuration."""
    seed: int = 42
    output_path: str = "results/physics_manifest.json"
    d0: D0ClusterConfig = field(default_factory=D0ClusterConfig)
    hg201: Hg201Config = field(default_factory=Hg201Config)
    spin_transfer: SpinTransferConfig = field(default_factory=SpinTransferConfig)
    gamma_511: Gamma511Config = field(default_factory=Gamma511Config)
    arxiv_id: str = "2608.09871"

    def to_dict(self):
        return {
            "seed": self.seed,
            "output_path": self.output_path,
            "arxiv_id": self.arxiv_id,
            "d0": self.d0.__dict__,
            "hg201": self.hg201.__dict__,
            "spin_transfer": self.spin_transfer.__dict__,
            "gamma_511": self.gamma_511.__dict__,
        }
