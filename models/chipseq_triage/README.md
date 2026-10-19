# models/chipseq_triage — H3K9ac / H3K56ac QC and triage

**Milestone 2 / D2.2.** See [`docs/ROADMAP_2026_2027.md`](../../docs/ROADMAP_2026_2027.md).
Licensed under Apache-2.0 ([`LICENSE`](LICENSE)), separately from the repository root.

Status: **scaffolding**. QC thresholds and output schema are fixed; the pipeline is not
implemented yet (`TODO` markers in source).

## Why this is a separate directory

The roadmap's Milestone 2 was split by data type. The methylation half
([`models/dunedin_pace/`](../dunedin_pace/)) calls a **GPL-3.0** reference implementation
across a process boundary. Keeping ChIP-seq QC in its own directory means that boundary
stays obvious to anyone reading the tree. This module has no GPL dependency.

## What this module does

Quality control and triage for public H3K9ac and H3K56ac ChIP-seq datasets — both reported
SIRT6 deacetylation substrates — before any association analysis runs:

| Check | Threshold | Source |
|-------|-----------|--------|
| Alignment quality | MAPQ ≥ 30 | [`config/datasets.yaml`](config/datasets.yaml) |
| Differential peak calling | FDR < 0.05 | same |
| Biological replicates | ≥ 3 | same |
| Input control | required | same |

## Running

```bash
pip install pyyaml
python models/chipseq_triage/triage.py --check
python models/chipseq_triage/triage.py
```

`datasets:` ships empty on purpose — add public accessions before running. Results are
written to `results/chipseq_triage/`.

## Interpretation limits

- Passing QC means a dataset is **usable**, not that it supports any hypothesis.
- Association between a histone mark and an epigenetic clock score is **not evidence of a
  causal relationship**, in either direction. Downstream analysis (D2.3) reports effect sizes
  with confidence intervals and sample sizes for this reason.
- Public data only; no new biological measurements are produced here.

## References

- Michishita, E. et al. (2008). SIRT6 is a histone H3 lysine 9 deacetylase that modulates
  telomeric chromatin. *Nature* 452:492–496.
- Michishita, E. et al. (2009). Cell cycle-dependent deacetylation of telomeric histone H3
  lysine K56 by human SIRT6. *Cell Cycle* 8:2664–2666.
- Zhang, Y. et al. (2008). Model-based analysis of ChIP-Seq (MACS). *Genome Biology* 9:R137.
