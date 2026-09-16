"""
Biorock Electrochemical Mineral Accretion Kinetics Simulator
Hyperion DeepTech Research Group / Synapse Core Infrastructure Initiative

Models:
  1. Nernst diffusion layer pH as a function of cathodic current density j
  2. Saturation indices Omega for aragonite (CaCO3) and brucite (Mg(OH)2)
  3. Faraday-driven self-healing kinetics for a 200 um microcrack

Units: SI throughout (A/m2, mol/L, hours)
License: Apache-2.0
"""

import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------
# Physical constants
# --------------------------------------------------------------------------
F = 96485.0       # Faraday constant, C/mol
R = 8.314         # Gas constant, J/(mol*K)
T = 298.15        # Temperature, K

# --------------------------------------------------------------------------
# Seawater bulk composition (mol/L)
# --------------------------------------------------------------------------
Ca2_bulk  = 10.3e-3   # Calcium
Mg2_bulk  = 53.2e-3   # Magnesium
HCO3_bulk =  2.1e-3   # Bicarbonate
pH_bulk   =  8.1

# --------------------------------------------------------------------------
# Solubility products
# --------------------------------------------------------------------------
Ksp_aragonite = 3.67e-9    # CaCO3 (aragonite)
Ksp_brucite   = 5.61e-12   # Mg(OH)2


def ph_boundary(j, delta_D=75e-6, D_OH=5.3e-9):
    """Estimate interfacial pH from Nernst diffusion layer model."""
    flux_OH = j / (2 * F)
    c_OH_excess = flux_OH * delta_D / D_OH
    c_OH = c_OH_excess / 1000.0 + 10**(pH_bulk - 14)
    c_OH = max(c_OH, 1e-7)
    return min(14 + np.log10(c_OH), 10.8)


def saturation_aragonite(pH):
    """Omega for CaCO3 (aragonite) given interfacial pH."""
    K2 = 4.69e-11
    Ka_water = 1e-14
    c_OH = 10**(pH - 14)
    c_CO3 = HCO3_bulk * (c_OH / (Ka_water / K2 + c_OH))
    return (Ca2_bulk * c_CO3) / Ksp_aragonite


def saturation_brucite(pH):
    """Omega for Mg(OH)2 (brucite) given interfacial pH."""
    c_OH = 10**(pH - 14)
    return (Mg2_bulk * c_OH**2) / Ksp_brucite


def healing_kinetics(j_crack=120.0, j_nominal=10.0,
                     crack_width_um=200.0, area_m2=1e-6,
                     eta=0.85, t_max_h=48.0):
    """Model current decay and fissure closure after crack event."""
    M_CaCO3   = 100.09e-3   # kg/mol
    rho_CaCO3 = 2930.0      # kg/m3
    z = 2

    crack_vol    = (crack_width_um * 1e-6) * area_m2
    mass_needed  = crack_vol * rho_CaCO3

    dt = 0.01
    t_arr, j_arr, closure_arr = [], [], []
    mass_deposited = 0.0
    t = 0.0

    while t <= t_max_h:
        remaining = max(1.0 - mass_deposited / mass_needed, 0.0)
        j_t = j_nominal + (j_crack - j_nominal) * remaining
        dm_dt = (M_CaCO3 * j_t * eta) / (z * F)
        dm = dm_dt * area_m2 * dt * 3600
        mass_deposited = min(mass_deposited + dm, mass_needed)
        t_arr.append(t)
        j_arr.append(j_t)
        closure_arr.append(mass_deposited / mass_needed * 100.0)
        t += dt

    return np.array(t_arr), np.array(j_arr), np.array(closure_arr)


if __name__ == '__main__':

    # Figure 1: pH and Omega vs j
    j_range = np.linspace(0, 25, 300)
    pH_arr  = [ph_boundary(j) for j in j_range]
    Om_arag = [saturation_aragonite(ph) for ph in pH_arr]
    Om_bru  = [saturation_brucite(ph)   for ph in pH_arr]

    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()

    ax1.plot(j_range, pH_arr,  'b-',  linewidth=2.5, label='Interfacial Boundary pH')
    ax2.plot(j_range, Om_arag, 'r-',  linewidth=2.5,
             label=r'Aragonite Saturation ($\Omega_{CaCO_3}$)')
    ax2.plot(j_range, Om_bru,  color='darkorange', linestyle='-.', linewidth=2.5,
             label=r'Brucite Saturation ($\Omega_{Mg(OH)_2}$)')

    ax1.axvspan(10, 15, alpha=0.12, color='green')
    ax2.axhline(1.0, color='gray', linestyle=':', linewidth=1)
    ax2.set_yscale('log')

    ax1.set_xlabel(r'Cathodic Current Density $j$ (A/m$^2$)', fontsize=12)
    ax1.set_ylabel('Interfacial Boundary pH', color='blue', fontsize=12)
    ax2.set_ylabel(r'Saturation State $\Omega$', fontsize=12)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='lower right', fontsize=10)
    plt.title('Figure 1: Electrochemical Boundary pH & Mineral Saturation vs. Current Density',
              fontweight='bold')
    plt.tight_layout()
    plt.savefig('figures/figure1_biorock_ph_saturation.png', dpi=150)
    plt.close()
    print('Figure 1 saved.')

    # Figure 2: Self-healing kinetics
    t_arr, j_arr, closure_arr = healing_kinetics()

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()

    ax1.plot(t_arr, j_arr,       'r-',  linewidth=2.5,
             label=r'Local Current Density ($j_{crack}$)')
    ax2.plot(t_arr, closure_arr, 'b--', linewidth=2.5,
             label='Autonomous Fissure Closure (%)')

    ax1.set_xlabel('Time Post-Fissure Event (hours)', fontsize=12)
    ax1.set_ylabel(r'Local Current Density $j_{crack}$ (A/m$^2$)', color='red', fontsize=12)
    ax2.set_ylabel('Fissure Closure / Aragonite Fill (%)', color='blue', fontsize=12)

    ax1.annotate(
        'Fissure Event (200 μm):\nBare Substrate Exposed\n'
        r'($R_{crack} \ll R_{surface}$)',
        xy=(0, 120), xytext=(4, 105),
        arrowprops=dict(arrowstyle='->', color='black'),
        fontsize=10, bbox=dict(boxstyle='round,pad=0.3', fc='#ffe0e0'))

    ax1.annotate(
        '100% Structural Closure\n(Current Density Recovers)',
        xy=(9.5, 10), xytext=(15, 38),
        arrowprops=dict(arrowstyle='->', color='black'),
        fontsize=10, bbox=dict(boxstyle='round,pad=0.3', fc='#e0ffe0'))

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=10)
    plt.title('Figure 2: Faraday-Driven Autonomous Self-Healing Kinetics in Biorock Matrix',
              fontweight='bold')
    plt.tight_layout()
    plt.savefig('figures/figure2_biorock_self_healing.png', dpi=150)
    plt.close()
    print('Figure 2 saved.')
