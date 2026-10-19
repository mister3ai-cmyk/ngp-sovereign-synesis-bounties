# Changelog

All notable changes to this repository are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This file starts at 2026-10-19; earlier history is in the git log.

Negative and null results are recorded here alongside positive ones.

## [Unreleased]

### Added

- `docs/ROADMAP_2026_2027.md` — three research milestones for months 1–9, with acceptance
  criteria and stated limitations for each.
- `core/sirt6_resonance/` — scaffolding for allosteric pocket docking against published SIRT6
  structures (5Y2F, 5MF6, 3K35, 5X16), with re-docking of known activators as positive
  controls. Apache-2.0.
- `models/dunedin_pace/` — scaffolding for DunedinPACE clock calibration on public methylation
  arrays. The GPL-3.0 reference implementation is invoked as an external process and is not
  vendored. Apache-2.0.
- `models/chipseq_triage/` — scaffolding for H3K9ac / H3K56ac ChIP-seq QC and triage, kept in
  its own directory so the GPL-3.0 boundary around the clock module stays visible. Apache-2.0.
- `safety/paleo_shield/` — scaffolding for in-silico dedifferentiation screening criteria,
  with `LIMITATIONS.md` stating that the module does not and cannot verify safety.
  Apache-2.0.
- `tests/test_scaffolding.py` — structural tests: configs parse, stubs import, every module
  carries its licence, the GPL boundary holds, and the safety disclaimers are still present.
- `CONTRIBUTING.md` — contribution scope, licensing split, DCO sign-off, claim discipline.
- CI job `Roadmap 2026-2027 — module scaffolding`, which runs lint and the structural tests
  and is not permitted to fail.

### Changed

- `papers/deeptech-proofs-04-epigenetic-anchor/README.md` — the results table is relabelled
  from "Key Results" to model predictions, and marked as an in-silico hypothesis that has not
  been experimentally validated. The numbers are unchanged; only their status is now stated.
- `README.md` — pull requests are accepted again for the roadmap modules; the licensing split
  between BSL 1.1 and Apache-2.0 is documented.

### Fixed

- 14 pre-existing lint errors in `tests/` reported by ruff: unsorted imports (6), unused
  imports (4), and `subprocess.run` without an explicit `check` argument (4). The four
  call sites use `check=False`, which preserves the existing behaviour: each one already
  inspects `returncode` itself and raises an assertion carrying the subprocess stderr,
  which `check=True` would pre-empt. Test outcomes are unchanged before and after
  (7/9/7 skipped, 9 and 9 passed). This clears the `Code Quality` CI job, which had been
  failing.

### Notes

- No scientific results are included in this change. Every module ships as scaffolding with
  its computation unimplemented (`TODO` markers in source).
- Thresholds in `safety/paleo_shield/criteria.py` are deliberately unset. The module refuses
  to evaluate a profile against an unsourced threshold.
