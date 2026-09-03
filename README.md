# NGP 3.0 Sovereign Synesis — Open DeSci Bounty Program

> ⚠️ **PROGRAMME CLOSED**
> This bounty programme has been officially closed. All research tracks are being absorbed into the **Syn Research Laboratory** internal pipeline. No new submissions are accepted. Thank you to everyone who showed interest.
>
> For collaboration inquiries, contact: research@syn.ai

---

## Overview

The **Sovereign Synesis Bounty Programme** was an open, permissionless research initiative governed by the NGP 3.0 decentralised knowledge protocol. Three high-priority scientific engineering tasks were funded at the intersection of longevity epigenomics, low-energy nuclear reaction (LENR) physics, and robotic laboratory automation.

**This programme is now closed. The research continues within Syn Research Laboratory.**

---

## Bounties — Status

| # | Title | Status |
|---|-------|--------|
| 1 | ChIP-seq & Methylation PACE Pipeline | 🔴 Closed |
| 2 | Karabut–FCQC Physical Simulator | 🔴 Closed |
| 3 | DryLab4 & SiLA 2 Robotic Bridge | 🔴 Closed |

---

## Bounty #1 — ChIP-seq & Methylation PACE Pipeline

### Scientific Context

SIRT6 is a NAD⁺-dependent histone deacetylase critically involved in DNA double-strand break repair, heterochromatin maintenance, and metabolic homeostasis. SIRT6 overexpression extends lifespan in multiple model organisms; conversely, its ablation produces a progeroid phenotype. The **DunedinPACE** clock (Belsky et al., 2022, *eLife*) measures the instantaneous pace of biological aging from blood methylome data and achieves a normalised intercept of **51.024577** (SD ≈ 7.3) in the CALERIE-2 cohort.

### Objective

Construct a fully reproducible, containerised bioinformatics pipeline that:

1. Processes raw FASTQ ChIP-seq reads for histone marks **H3K9ac** and **H3K56ac** — both direct SIRT6 deacetylation substrates — across ≥ 3 biological replicates.
2. Computes DunedinPACE epigenetic aging scores from paired WGBS or 450K/EPIC array methylation data.
3. Demonstrates a statistically significant correlation (Pearson **r > 0.92**, p < 0.01) between differential H3K9ac/H3K56ac occupancy at SIRT6 target loci and DunedinPACE score.

### Acceptance Criteria

```
✅ DunedinPACE intercept == 51.024577 ± 0.001 on reference dataset
✅ H3K9ac peak-to-DunedinPACE Pearson r > 0.92
✅ H3K56ac peak-to-DunedinPACE Pearson r > 0.92
✅ Pipeline reproducible from FASTQ → final report in single `nextflow run` or `snakemake` command
✅ Docker/Singularity image passes `md5sum` checksum verification
✅ All intermediate BAM files flagged with MAPQ ≥ 30 filter applied
✅ FDR < 0.05 on differential peak calling (MACS3 or equivalent)
```

---

## Bounty #2 — Karabut–FCQC Physical Simulator

### Scientific Context

Alexander Karabut's glow-discharge experiments (IAEA Technical Reports, 1995–2004) reported anomalous soft X-ray emission (Hg-201 line at **1564.8 keV**) and excess heat in deuterium-loaded Pd cathodes. Holmlid & Zeiner-Gundersen (2019, *Int. J. Hydrogen Energy*) characterised **Deuterium(0)** — an ultra-dense hydrogen isotopologue with internuclear distance **d = 2.3 pm** — as a candidate precursor for LENR. The Fractional Charge Quantum Coherence (FCQC) hypothesis proposes that quasi-free electrons in sub-Ångström geometries enable nuclear screening sufficient for sub-Coulomb-barrier fusion.

### Objective

Develop a physics simulation code that:

1. Reproduces the **Hg-201 transition at 1564.8 keV** from first-principles quantum electrodynamic (QED) or density-functional perturbation-theory (DFPT) calculations.
2. Models D(0) cluster formation with equilibrium bond length **2.3 pm ± 0.05 pm**.
3. Achieves **Spin-Transfer efficiency (ST-efficiency) ≥ 0.92** at damping coefficient **κ = 16.6 ps⁻¹** in the Karabut glow-discharge geometry.
4. Predicts the **511 keV positron-annihilation gamma line** intensity within 15% of experimentally reported values.

---

## Bounty #3 — DryLab4 & SiLA 2 Robotic Bridge

### Scientific Context

Systematic longevity drug discovery requires automated, reproducible experimental execution at scale. **SiLA 2** (Standardisation in Lab Automation 2, ISO 23166) defines a gRPC-based protocol for vendor-neutral instrument control. The **DryLab4** chromatography modelling engine (LCCC, Vienna) provides first-principles retention-time predictions enabling in-silico HPLC method development without wet-lab iteration.

### Objective

Deliver a production-ready middleware layer that:

1. Exposes Hamilton Microlab STARlet as a **SiLA 2 Feature** (gRPC service with `.proto` definition conforming to SiLA 2 v1.0.0).
2. Bridges DryLab4 method predictions to automated HPLC runs via the SiLA 2 transport, synchronising method parameters bi-directionally.
3. Integrates result acquisition from **Waters Empower** or **Agilent OpenLab CDS** into a unified run record.
4. Synchronises all instrument clocks and log timestamps to a **432 Hz master clock** reference.
5. Complies with **ICH Q14** analytical procedure development guidelines for data integrity and audit trail requirements.

---

## Evaluation Committee

| Role | Handle |
|------|--------|
| Protocol Lead | @mister3ai-cmyk |
| Longevity Science | TBD |
| Nuclear Physics | TBD |
| Lab Automation | TBD |

---

## References

- Belsky, D.W. et al. (2022). DunedinPACE: a DNA methylation biomarker of the pace of aging. *eLife*, 11, e73420.
- Karabut, A.B. et al. (1995). Nuclear products ratio for glow discharge in deuterium. *Il Nuovo Cimento*, 107A, 879.
- Holmlid, L. & Zeiner-Gundersen, S. (2019). Ultradense protium p(0) and deuterium D(0) and their relation to ordinary Rydberg matter. *Physica Scripta*, 74.
- SiLA 2 Consortium (2020). SiLA 2 Core Standard v1.0.0. https://sila-standard.com
- ICH Q14 (2023). Analytical Procedure Development. International Council for Harmonisation.
- NGP 3.0 Protocol Specification (2026). Syn Research Lab. Internal document.

---

*Research continues within Syn Research Laboratory. All previously submitted work is attributed in the NGP knowledge graph.*

---

## Repository Contents

| File | Description |
|------|-------------|
| [`sovereign_materials_optimizer_v3.py`](sovereign_materials_optimizer_v3.py) | Minnealloy thermodynamic phase optimiser (Birch-Murnaghan EOS + Grüneisen phonon softening) |
| [`docs/sovereign-materials-optimizer-tz-v3.md`](docs/sovereign-materials-optimizer-tz-v3.md) | Full scientific-technical specification |
| [`docs/crystallized-knowledge-enclaves.md`](docs/crystallized-knowledge-enclaves.md) | Crystallised interdisciplinary knowledge enclaves (NGP v4.5) |
| [`tests/test_materials_optimizer.py`](tests/test_materials_optimizer.py) | Automated validation suite |
| [`requirements.txt`](requirements.txt) | Python dependencies |

Run tests locally:
```bash
pip install numpy scipy
python -m unittest tests/test_materials_optimizer.py -v
```

---

## Licensing

This project is licensed under the **Apache License, Version 2.0**.  
You may not use this file except in compliance with the License. You may obtain a copy at:

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

### Patent Grant & Defense Commitment

By utilising or contributing to this repository under the Apache 2.0 license, you are granted a royalty-free, perpetual patent license by the authors. This license includes a reciprocal defense clause: any patent litigation instituted against Synapse Core or its contributors automatically terminates all patent rights granted to you under this license. We protect open-source innovation from corporate patent aggression.

### NGP 4.5 Marketplace Integration

The computational modules in this repository are registered as knowledge enclaves in the **NGP 4.5 Decentralised Knowledge Marketplace** (category: `System Utilities / Materials Science`). All accepted submissions and derivative works are attributed on-chain via the NGP provenance protocol.