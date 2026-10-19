# models/dunedin_pace — epigenetic clock calibration

**Milestone 2 / D2.1.** See [`docs/ROADMAP_2026_2027.md`](../../docs/ROADMAP_2026_2027.md).
Licensed under Apache-2.0 ([`LICENSE`](LICENSE)), separately from the repository root.

Status: **scaffolding**. Configuration and output schema are fixed; scoring is not
implemented yet (`TODO` markers in source).

## Licensing boundary — read before contributing

The reference implementation, [`danbelsky/DunedinPACE`](https://github.com/danbelsky/DunedinPACE),
is **GPL-3.0**. The harness in this directory is **Apache-2.0**.

These licences do not combine in one program. The boundary is kept by invoking the reference
implementation **as a separate process** through `Rscript`:

- it is never imported, linked, vendored, or copied into this repository;
- the version of the installed package is recorded with every result;
- contributors must not inline any part of that package here.

If you prefer not to maintain that boundary, the alternative is to license a derived pipeline
under GPL-3.0 and keep it in a separate repository.

## What this module does

Calibrates and characterises drift of the DunedinPACE clock (Belsky et al. 2022,
*eLife* 11:e73420) on **public** methylation array data (450K/EPIC) from GEO, and verifies
that recomputed scores agree with the reference implementation within the tolerance set in
[`config/cohorts.yaml`](config/cohorts.yaml).

## Running

```bash
pip install pyyaml
python models/dunedin_pace/run_pace.py --check    # validate config, R, and package version
python models/dunedin_pace/run_pace.py            # score configured cohorts
```

`cohorts:` ships empty on purpose — add public GEO accessions before running. Results are
written to `results/dunedin_pace/`.

## Interpretation limits

- DunedinPACE is a **statistical predictor trained on specific cohorts** (CALERIE / Dunedin).
  Scores do not transfer automatically to other tissues, platforms, ancestries, or age ranges.
- A change in clock score is **not** a measured change in health, lifespan, or disease risk.
  It is a change in a predictor's output.
- This module analyses existing public data only. It produces no new biological measurements
  and supports no claim about any intervention.
- Only public accessions are used. No controlled-access or individual-level restricted data.
