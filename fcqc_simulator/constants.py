"""
Physical constants and reference parameters for Karabut-FCQC simulation.
All values are in SI units unless explicitly annotated with energy/length units.
"""


# Fundamental Constants (CODATA 2022)
HBAR = 1.054571817e-34       # J*s (Reduced Planck constant)
HBAR_EV_S = 6.582119569e-16  # eV*s
C_LIGHT = 299792458.0        # m/s (Speed of light)
E_CHARGE = 1.602176634e-19   # C (Elementary charge)
EPSILON_0 = 8.8541878128e-12 # F/m (Vacuum permittivity)
M_ELECTRON = 9.1093837015e-31 # kg (Electron mass)
M_ELECTRON_KEV = 510.998950  # keV/c^2
M_DEUTERON = 3.3435837724e-27 # kg (Deuteron mass)
M_PROTON = 1.67262192369e-27  # kg (Proton mass)
A_BOHR = 5.29177210903e-11   # m (Bohr radius: 52.9177 pm)
FINE_STRUCTURE = 7.2973525643e-3 # alpha ≈ 1/137.035999

# Acceptance Criteria Targets
HG201_TARGET_KEV = 1564.8
HG201_TOLERANCE_KEV = 0.5

D0_BOND_TARGET_PM = 2.30
D0_BOND_TOLERANCE_PM = 0.05

KAPPA_TARGET_PS = 16.6
ST_EFFICIENCY_TARGET_MIN = 0.92

GAMMA_511_REFERENCE = 1.0
GAMMA_511_TOLERANCE_FRACTION = 0.15

# Ultradense Deuterium Fractional Quantum Numbers (Holmlid 2019)
# s=1: ground ultradense state d ≈ 0.56 pm
# s=2: metastable spin-paired state d ≈ 2.30 pm
D0_FRACTIONAL_S1_PM = 0.56
D0_FRACTIONAL_S2_PM = 2.30
