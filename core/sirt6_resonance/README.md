# core/sirt6_resonance — allosteric pocket characterisation and docking

**Milestone 1 (months 1–3).** See [`docs/ROADMAP_2026_2027.md`](../../docs/ROADMAP_2026_2027.md).
Licensed under Apache-2.0 ([`LICENSE`](LICENSE)), separately from the repository root.

Status: **scaffolding**. Configuration, output schema and provenance fields are fixed;
the docking and normal-mode computations are not implemented yet (`TODO` markers in source).

## What this module does

Docks ligands into the experimentally characterised allosteric pocket of SIRT6 using
published structures, and reports pocket geometry alongside an exploratory normal-mode
analysis.

| Structure | Contents | Role |
|-----------|----------|------|
| [5Y2F](https://www.rcsb.org/structure/5Y2F) | SIRT6 + allosteric activator MDL-801 | positive control |
| [5MF6](https://www.rcsb.org/structure/5MF6) | SIRT6 + activator UBCS039 | positive control |
| [3K35](https://www.rcsb.org/structure/3K35) | Human SIRT6 | reference |
| [5X16](https://www.rcsb.org/structure/5X16) | SIRT6 apo | reference |

The positive controls come first: if re-docking a known activator into its own crystal
structure does not recover the crystallographic pose within the RMSD threshold in
[`config/docking.yaml`](config/docking.yaml), the setup is wrong and nothing downstream is
interpretable.

## Running

Requires an external docking binary (AutoDock Vina or smina). It is invoked as a separate
process and is not bundled with this repository.

```bash
pip install pyyaml
python core/sirt6_resonance/dock_pocket.py --check     # validate config and environment
python core/sirt6_resonance/dock_pocket.py             # run docking
python core/sirt6_resonance/normal_modes.py            # exploratory mode analysis
```

Results are written to `results/sirt6_resonance/`.

## What this module does not do

- **Docking scores are not binding free energies.** They are ranking heuristics whose
  absolute agreement with experiment is routinely poor. Use them to order candidates within
  a single run, not to state affinity.
- **The normal-mode analysis is exploratory.** Low-frequency modes are a structural
  observable of the elastic network. There is no established causal link between them and
  SIRT6 catalytic activation, and computing them does not create one. Testing such a link
  would require spectroscopic and enzymatic experiments that are outside this repository.
- **Nothing here demonstrates activation of SIRT6 by light, terahertz radiation, or any
  other non-chemical means.** The module name refers to vibrational modes in a structural
  model, not to a demonstrated activation mechanism.
- No wet-lab work, no cell data, no therapeutic claim.

## References

- Huang, Z. et al. (2018). Identification of a cellularly active SIRT6 allosteric activator.
  *Nature Chemical Biology* 14:1118–1126.
- You, W. et al. (2017). Structural basis of sirtuin 6 activation by synthetic small
  molecules. *Angewandte Chemie International Edition*.
- Trott, O. & Olson, A.J. (2010). AutoDock Vina. *J. Comput. Chem.* 31:455–461.
