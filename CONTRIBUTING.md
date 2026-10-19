# Contributing

Contributions are accepted for the **2026–2027 research roadmap modules** only:

| Path | Milestone |
|------|-----------|
| [`core/sirt6_resonance/`](core/sirt6_resonance/) | M1 — allosteric pocket docking |
| [`models/dunedin_pace/`](models/dunedin_pace/) | M2 — epigenetic clock calibration |
| [`models/chipseq_triage/`](models/chipseq_triage/) | M2 — ChIP-seq QC and triage |
| [`safety/paleo_shield/`](safety/paleo_shield/) | M3 — screening criteria |

See [`docs/ROADMAP_2026_2027.md`](docs/ROADMAP_2026_2027.md) for scope and acceptance criteria.

**The bounty programme has ended.** No submissions are accepted against the historical
bounty issues (#1–#3) and no payouts will be made. Those issues remain open as a record of
the research tracks.

## Licensing

| Area | Licence |
|------|---------|
| `core/`, `models/`, `safety/` | Apache-2.0 (each directory carries its own `LICENSE`) |
| Everything else | Business Source License 1.1 (root [`LICENSE`](LICENSE)) |

By opening a pull request against the roadmap modules you agree that your contribution is
licensed under Apache-2.0, and you certify the [Developer Certificate of Origin](https://developercertificate.org/)
by signing off each commit:

```bash
git commit -s -m "feat(core): ..."
```

**Do not vendor GPL-licensed code into this repository.** The DunedinPACE reference
implementation is GPL-3.0 and is invoked as an external process on purpose; see
[`models/dunedin_pace/README.md`](models/dunedin_pace/README.md). A pull request that
imports, copies, or links it will be declined regardless of its quality.

## Claim discipline

This repository is reviewed by people who will check the claims. Pull requests are read with
that in mind:

1. **Separate measurement from model output.** A number produced by a simulation is labelled
   as such, everywhere it appears, including in a README table.
2. **No medical or safety claims.** Nothing here diagnoses, treats, or prevents anything, and
   no computational result establishes safety. `safety/paleo_shield/` computes screening
   criteria; see its [`LIMITATIONS.md`](safety/paleo_shield/LIMITATIONS.md).
3. **Thresholds carry sources.** A numeric threshold without a traceable citation will not be
   merged. The code enforces this where it can.
4. **Report negative results.** A milestone that fails its acceptance criteria is written up
   in the `CHANGELOG.md` the same as one that passes.
5. **Public data only** for the current milestones; list every accession in the module config.

## Commits and pull requests

Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[body]
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`.
Scopes: `core`, `models`, `safety`, `roadmap`, `docs`, `ci`.

Before opening a pull request:

```bash
pip install pytest pyyaml ruff
ruff check core/ models/ safety/ tests/test_scaffolding.py
pytest tests/test_scaffolding.py -v
```

Both must pass. The `Roadmap 2026-2027 — module scaffolding` CI job runs the same commands
and, unlike the historical bounty jobs, it is not allowed to fail.

Describe in the pull request what you ran, on what data, and what the result was — including
the parts that did not work.

## Contact

research@syn.ai
