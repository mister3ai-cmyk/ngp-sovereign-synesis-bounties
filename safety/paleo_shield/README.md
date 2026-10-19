# safety/paleo_shield — in-silico screening criteria for dedifferentiation triage

**Milestone 3 (months 7–9).** See [`docs/ROADMAP_2026_2027.md`](../../docs/ROADMAP_2026_2027.md).
Licensed under Apache-2.0 ([`LICENSE`](LICENSE)), separately from the repository root.

> **This module does not verify safety.** It computes numerical screening criteria over
> simulated or published data. It cannot establish that anything is safe or non-oncogenic.
> Read [`LIMITATIONS.md`](LIMITATIONS.md) before citing any output from this directory.

Status: **scaffolding**. The constraint structure is in place; thresholds are deliberately
unset until each one has a literature source.

## What this module does

Partial reprogramming approaches carry a documented risk of loss of cell identity
(Ocampo et al. 2016, *Cell* 167:1719–1733). This module formalises numerical criteria that
**flag** trajectories drifting toward a dedifferentiated state, so that candidates can be
triaged computationally before anything reaches a bench.

| Criterion | Detects | Direction |
|-----------|---------|-----------|
| `pou5f1_expression` | OCT4/POU5F1 pluripotency marker | flag if above threshold |
| `nanog_expression` | NANOG pluripotency marker | flag if above threshold |
| `sox2_expression` | SOX2 pluripotency marker | flag if above threshold |
| `lineage_identity_score` | loss of the starting somatic programme | flag if below threshold |
| `trajectory_divergence` | drift from the somatic attractor basin | flag if above threshold |

## Why the thresholds are empty

Every `Constraint` requires a `threshold` **and** a `source` before it can be applied.
`evaluate()` raises `UnsourcedThreshold` rather than silently using a number that nobody can
trace to a publication. This is deliberate: an unsourced threshold in a module named
"safety" is worse than no threshold at all.

Populating them is part of D3.1, and each value must land together with its citation and the
assumptions (tissue, platform, normalisation) that make it meaningful.

## Running

```bash
python safety/paleo_shield/criteria.py     # lists constraints and what is still unsourced
```

## Benchmark

D3.3 ships a public labelled benchmark and reports the **false-negative rate** explicitly.
A screen that never misses within its own benchmark is reported as untested, not as perfect.

## References

- Ocampo, A. et al. (2016). In vivo amelioration of age-associated hallmarks by partial
  reprogramming. *Cell* 167:1719–1733.
- Abad, M. et al. (2013). Reprogramming in vivo produces teratomas and iPS cells with
  totipotency features. *Nature* 502:340–345.
- Waddington, C.H. (1957). *The Strategy of the Genes* (origin of the epigenetic-landscape
  framing used for trajectory divergence).
