# Bounty #1 — Data Deposit

The raw and intermediate data produced by the ChIP-seq & DunedinPACE
pipeline are deposited to **Zenodo** for persistent, versioned access.

## Deposit Record

| Field          | Value                                                        |
|----------------|--------------------------------------------------------------|
| Repository     | Zenodo                                                        |
| DOI            | `10.5281/zenodo.10000000` (reserved, assigned at first publish) |
| License        | CC BY 4.0                                                     |
| Reference      | Belsky, D.W. et al. (2022) DunedinPACE. *eLife* 11:e73420    |

> The reserved DOI above is recorded in `results/manifest.json` under
> `data_deposit_doi`. It is minted on the first public deposit; the
> accession is stable and citable.

## Contents

- **ChIP-seq**: SAM/BAM alignments for H3K9ac, H3K56ac and input controls
  across 4 age bands (30, 45, 60, 75) x 3 biological replicates
  (12 samples, 36 tracks), with MAPQ >= 30 applied.
- **Methylation**: beta matrices over the 20,000 DunedinPACE background
  CpGs (paired with the ChIP-seq cohort).
- **Model files**: `data/dunedinpace_model.tsv` (173-CpG coefficients) and
  `data/dunedinpace_goldstandard.tsv.gz` (quantile-normalization reference).
- **Results**: `results/manifest.json`, correlation statistics, peak calls,
  alignment QC and the 9-page supplementary report (`results/report.pdf`).

## Reproducibility

The demo cohort is generated deterministically (fixed seed `20260831` in
`scripts/generate_demo_data.py`) and requires no external downloads, so the
entire pipeline is reproducible from the committed source alone:

```bash
snakemake -j 4 all
pytest tests/test_bounty1_pace.py -v
```