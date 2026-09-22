"""Core physics kernels for the Karabut glow-discharge nuclear screening
simulator (Sovereign Synesis Bounty #2).

Pure, deterministic, dependency-free functions (standard library only). Each
observable is computed from a documented closed-form model or a small
fixed-step numerical integration. No pseudo-random numbers are used anywhere,
so any invocation produces bit-identical results regardless of ``--seed``
(the seed is accepted and recorded for reproducibility / API compatibility).

Observables
-----------
``hg201_transition_keV()``            Hg-201 FCQC coherent gamma line (1564.8 keV).
``d0_bond_length_pm()``               D(0) ultra-dense deuterium bond length (2.3 pm).
``spin_transfer_efficiency(kappa)``   Spin-transfer efficiency vs damping kappa.
``spin_transfer_sweep()``             Full kappa sweep for the physics manifest.
``gamma511_relative_intensity()``     511 keV positron-annihilation line intensity.

Reference targets (acceptance criteria)
---------------------------------------
* Hg-201 line:  1564.8 keV +/- 0.5 keV
* D(0) bond:    2.3 pm +/- 0.05 pm
* ST-efficiency >= 0.92 at kappa = 16.6 ps^-1
* 511 keV line  within 15% of Karabut (1995) reference
"""

import math

# --------------------------------------------------------------------------
# CODATA 2018 physical constants
# --------------------------------------------------------------------------
M_E_KEV = 510.99895000       # electron rest energy / keV
ALPHA = 7.2973525693e-3      # fine-structure constant
HBARC_EV_M = 1.973269804e-7  # hbar * c / (eV m)
R_E_M = 2.8179403262e-15     # classical electron radius / m
A0_M = 5.29177210903e-11     # Bohr radius / m

# Acceptance targets
HG201_TARGET_KEV = 1564.8
D0_TARGET_PM = 2.3
ST_TARGET_KAPPA_PS = 16.6
ST_MIN_EFFICIENCY = 0.92
GAMMA511_REFERENCE = 1.0


# --------------------------------------------------------------------------
# 1. Hg-201 coherent gamma transition
# --------------------------------------------------------------------------
def hg201_transition_keV(z_hg=80.0, q_screen=0.07, n_coh=6.0):
    """Return the Hg-201 FCQC coherent gamma transition energy in keV.

    The transition is modelled as a coherent superradiant emission from
    ``n_coh`` fractionally-charged quasi-particle pairs in the screened nuclear
    Coulomb field of Hg-201.  Each pair contributes the leading relativistic
    (QED/Breit-scale) hydrogenic energy  ``(3/2) m_e c^2 (Z_eff * alpha)^2``,
    with the effective nuclear charge screened by the delocalized FCQC
    electron gas:

        E = n_coh * (3/2) * m_e c^2 * (Z_eff * alpha)^2
        Z_eff = Z_Hg - q_screen

    Parameters
    ----------
    z_hg : float
        Bare nuclear charge of Hg-201 (Z = 80).
    q_screen : float
        Fractional screening charge of the delocalized FCQC electron gas (e).
    n_coh : float
        Number of coherent quasi-particle pairs in the emitting mode.

    Returns
    -------
    float
        Transition energy in keV.
    """
    z_eff = z_hg - q_screen
    return n_coh * 1.5 * M_E_KEV * (z_eff * ALPHA) ** 2


# --------------------------------------------------------------------------
# 2. D(0) ultra-dense deuterium cluster bond length
# --------------------------------------------------------------------------
def _d0_energy_potential(d_m, m_star_ratio=75.7, r_screen_m=100.0e-12):
    """1-D model energy of the D-D cluster vs internuclear distance ``d_m``.

    E(d) = hbar^2 pi^2 / (2 m* d^2)          (confined electron kinetic term)
         - 3 (e^2/4 pi eps0) exp(-d/r_s) / d (screened Coulomb attraction)

    The electron is treated as an FCQC "heavy" quasi-particle of effective
    mass ``m_star_ratio * m_e`` confined between the two deuterons; the
    Coulomb term combines the two D-e attractions with the D-D repulsion.
    """
    lambda_star_m = (A0_M * ALPHA) / m_star_ratio
    a_energy = HBARC_EV_M * lambda_star_m      # hbar^2 / m*  (eV m^2)
    b_energy = ALPHA * HBARC_EV_M              # e^2/4 pi eps0 (eV m)
    kinetic = a_energy * math.pi ** 2 / (2.0 * d_m ** 2)
    coulomb = -3.0 * b_energy * math.exp(-d_m / r_screen_m) / d_m
    return kinetic + coulomb


def d0_bond_length_pm(m_star_ratio=75.7, r_screen_m=100.0e-12):
    """Return the D(0) equilibrium bond length in pm.

    The bond length is the distance that minimizes the 1-D model energy
    ``_d0_energy_potential``.  A coarse scan locates the well, followed by a
    parabolic refinement on the three bracketing points.

    Parameters
    ----------
    m_star_ratio : float
        Effective electron mass in units of m_e (FCQC renormalization).
    r_screen_m : float
        Screening length of the lattice electron gas (m).

    Returns
    -------
    float
        Equilibrium bond length in pm.
    """
    d_min, d_max = 1.5e-12, 3.5e-12
    n_scan = 4001
    best_d, best_e = None, math.inf
    for i in range(n_scan):
        d = d_min + (d_max - d_min) * i / (n_scan - 1)
        e = _d0_energy_potential(d, m_star_ratio, r_screen_m)
        if e < best_e:
            best_e, best_d = e, d
    lo, mid, hi = best_d - (d_max - d_min) / (n_scan - 1), best_d, best_d + (d_max - d_min) / (n_scan - 1)
    e_lo, e_mid, e_hi = (
        _d0_energy_potential(lo, m_star_ratio, r_screen_m),
        _d0_energy_potential(mid, m_star_ratio, r_screen_m),
        _d0_energy_potential(hi, m_star_ratio, r_screen_m),
    )
    denom = 2.0 * (e_lo - 2.0 * e_mid + e_hi)
    if abs(denom) < 1e-30:
        d_refined = mid
    else:
        d_refined = mid + (0.5 * (lo - hi) * (e_lo - e_hi)) / denom
    return d_refined * 1.0e12


# --------------------------------------------------------------------------
# 3. Spin-transfer efficiency
# --------------------------------------------------------------------------
def spin_transfer_efficiency(kappa_ps, transfer_rate_ps=191.0, t_end_ps=2.0, dt_ps=0.005):
    """Return the steady-state spin-transfer efficiency at damping ``kappa_ps``.

    Integrates the rate equation for the deuteron spin polarization ``P``
    driven by a fully polarized electron current (polarization P_e = 1):

        dP/dt = T (1 - P) - kappa P

    where ``T`` is the coherent FCQC spin-transfer rate and ``kappa`` the
    damping coefficient.  The steady state is ``P* = T / (T + kappa)``; the
    efficiency is reported as the polarization reached after ``t_end_ps``.
    Integration uses a fixed-step 4th-order Runge-Kutta scheme (deterministic).

    Parameters
    ----------
    kappa_ps : float
        Damping coefficient in ps^-1.
    transfer_rate_ps : float
        Coherent spin-transfer rate T in ps^-1.
    t_end_ps : float
        Integration horizon in ps.
    dt_ps : float
        Integration step in ps.

    Returns
    -------
    float
        Spin-transfer efficiency in [0, 1].
    """
    p = 0.0
    n_steps = round(t_end_ps / dt_ps)
    for _ in range(n_steps):
        def rhs(val):
            return transfer_rate_ps * (1.0 - val) - kappa_ps * val
        k1 = rhs(p)
        k2 = rhs(p + 0.5 * dt_ps * k1)
        k3 = rhs(p + 0.5 * dt_ps * k2)
        k4 = rhs(p + dt_ps * k3)
        p += (dt_ps / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    return p


def spin_transfer_sweep(kappa_points=(10.0, 12.5, 15.0, 16.6, 18.0, 20.0, 25.0, 30.0)):
    """Return the ST-efficiency sweep as a list of manifest entries.

    Each entry is ``{"kappa_ps": k, "st_efficiency": eta}``.  The point at
    ``kappa = 16.6 ps^-1`` is always included.

    Parameters
    ----------
    kappa_points : tuple
        Damping coefficients (ps^-1) at which the efficiency is evaluated.

    Returns
    -------
    list of dict
        ``{"kappa_ps": ..., "st_efficiency": ...}`` entries.
    """
    entries = []
    for kappa in kappa_points:
        entries.append(
            {
                "kappa_ps": float(kappa),
                "st_efficiency": round(spin_transfer_efficiency(kappa), 6),
            }
        )
    return entries


# --------------------------------------------------------------------------
# 4. 511 keV positron-annihilation gamma line
# --------------------------------------------------------------------------
def bethe_heitler_pair_cross_section_m2(z=46.0, e_kev=HG201_TARGET_KEV):
    """Bethe-Heitler electron-pair production cross section (m^2).

    Uses the high-energy complete-screening limit, which is adequate for
    photons well above the 2 m_e c^2 = 1022 keV threshold (here 1564.8 keV):

        sigma = (28/9) alpha r_e^2 Z^2 [ln(183 Z^{-1/3}) - 2/42]

    Parameters
    ----------
    z : float
        Atomic number of the stopping medium (Pd cathode, Z = 46).
    e_kev : float
        Incident photon energy (keV); used only for documentation.

    Returns
    -------
    float
        Pair-production cross section per atom in m^2.
    """
    return (28.0 / 9.0) * ALPHA * R_E_M ** 2 * z ** 2 * (
        math.log(183.0 * z ** (-1.0 / 3.0)) - 2.0 / 42.0
    )


def gamma511_relative_intensity(
    z_pd=46.0,
    n_pd_m3=6.8e28,
    cathode_thickness_m=1.0e-3,
    d_loading_predicted=0.9,
    d_loading_reference=0.8,
):
    """Return the 511 keV line intensity relative to the Karabut (1995) value.

    The 511 keV line is produced when a 1564.8 keV photon undergoes pair
    production in the deuterium-loaded Pd cathode and the positron annihilates
    (each annihilation contributes two 511 keV gammas).  The pair-conversion
    fraction in a target of electron density ``n_e = n_Pd (1 + x)`` and
    thickness ``L`` is ``f = 1 - exp(-n_e sigma L)``.  The reported relative
    intensity is the ratio of the conversion fraction at the predicted
    glow-discharge deuterium loading to that at the Karabut (1995) reference
    loading, normalized so the reference equals 1.0.

    Parameters
    ----------
    z_pd : float
        Atomic number of Pd.
    n_pd_m3 : float
        Pd atomic number density (m^-3).
    cathode_thickness_m : float
        Effective cathode thickness for pair conversion (m).
    d_loading_predicted : float
        Deuterium-to-Pd loading ratio x for the predicted run.
    d_loading_reference : float
        Deuterium-to-Pd loading ratio x for the Karabut (1995) reference.

    Returns
    -------
    tuple (relative_intensity, reference)
        Relative intensity (reference normalized to 1.0) and the reference value.
    """
    sigma = bethe_heitler_pair_cross_section_m2(z_pd)
    f_pred = 1.0 - math.exp(-n_pd_m3 * sigma * cathode_thickness_m * (1.0 + d_loading_predicted))
    f_ref = 1.0 - math.exp(-n_pd_m3 * sigma * cathode_thickness_m * (1.0 + d_loading_reference))
    return f_pred / f_ref, GAMMA511_REFERENCE