# Electrochemical Seawater Mineral Accretion Dynamics

**Potentiostatic Control, Phase Thermodynamics, and Self-Healing Kinetics of Biorock Substructures**

*Hyperion DeepTech Research Group / Synapse Core Infrastructure Initiative*  
*Published: September 2026*

> DOI badge will appear here after Zenodo upload:  
> `[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)`

---

## Abstract

Conventional marine concrete ($2.5B–$3.0B CAPEX) suffers entropy-driven degradation within 25–40 years. This paper presents a first-principles physical model for low-voltage potentiostatic electro-accretion (Biorock, 1.2–2.4 V DC) that achieves:

- **Thermodynamic phase selectivity**: aragonite CaCO₃ (80–120 MPa) at j ≤ 15 A/m², while brucite Mg(OH)₂ is suppressed (pH < 9.5)
- **Autonomous self-healing**: 200 µm microcracks sealed in **9.5 hours** via Faraday feedback (j_crack ≈ 120 A/m²)
- **CAPEX arbitrage**: $850M–$1.1B vs $2.5B–$3.0B → **>$1.5B saving** per 50-hectare project
- **ESG**: Carbon-mineralizing asset, 100-year design life, no chloride degradation

---

## Key Findings

| Metric | Value |
|---|---|
| Optimal current window | j = 10–15 A/m² |
| Aragonite compressive strength | 80–120 MPa |
| Self-healing time (200 µm crack) | 9.5 hours |
| Energy consumption | ~1.8 kWh/kg CaCO₃ |
| CAPEX savings vs conventional | >$1.5B per project |

---

## Repository Structure

```
papers/deeptech-proofs-01-biorock/
├── README.md
├── main.tex                                   # LaTeX source (IEEEtran format)
├── Electrochemical_Seawater_Accretion_v4.pdf  # Compiled PDF
├── simulation/
│   └── biorock_kinetics.py                    # Faraday kinetics simulator
├── figures/
│   ├── figure1_biorock_ph_saturation.png
│   └── figure2_biorock_self_healing.png
└── LICENSE
```

---

## Compilation

```bash
pdflatex main.tex
pdflatex main.tex
```

Requires: `IEEEtran`, `amsmath`, `graphicx`, `booktabs`, `hyperref`, `microtype`

---

## Citation

```bibtex
@article{hyperion2026biorock,
  title   = {Electrochemical Seawater Mineral Accretion Dynamics: Potentiostatic Control,
             Phase Thermodynamics, and Self-Healing Kinetics of Biorock Substructures},
  author  = {{Hyperion DeepTech Research Group} and {Synapse Core Infrastructure Initiative}},
  year    = {2026},
  month   = {September},
  url     = {https://github.com/mister3ai-cmyk/ngp-sovereign-synesis-bounties}
}
```

---

## License

Apache License 2.0 — see [LICENSE](LICENSE)
