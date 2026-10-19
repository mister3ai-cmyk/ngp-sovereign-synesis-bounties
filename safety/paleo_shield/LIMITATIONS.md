# Limitations — read before citing this module

## This module does not verify safety

`safety/paleo_shield/` computes **numerical screening criteria** over simulated trajectories
and published expression data. That is all it does.

It **cannot** establish that any intervention, compound, or protocol is safe, non-oncogenic,
tolerable, or fit for use in any organism. No output of this module may be described as a
safety verification, a safety guarantee, or evidence of safety.

The name "Paleo-Shield" is a **project codename for a computational module**. It is not a
claim of protection, and it should not be read as one.

## What an actual oncogenic-risk assessment requires

None of the following is in scope for this repository, and no output here substitutes for
any of it:

1. **Cell-based assays** — karyotype analysis, soft-agar colony formation, proliferation and
   senescence assays, lineage-marker panels across passages.
2. **In-vivo studies** — long-term tumour-incidence studies in appropriate animal models,
   with histopathology and adequate follow-up duration and group sizes.
3. **Independent replication** — by a laboratory with no stake in the result.
4. **Regulated clinical investigation** — under the applicable regulatory framework, with
   ethical review, informed consent, and pre-registered endpoints.

A computational screen sits before step 1. It can suggest where to look. It cannot tell you
that something is safe.

## Specific limitations of the criteria

- **Thresholds ship unset.** Every `Constraint` requires a literature-sourced value and a
  record of the assumptions (tissue, platform, normalisation) under which it is meaningful.
  `evaluate()` refuses to run against an unsourced threshold rather than apply an untraceable
  number. Until they are populated from cited sources, this module produces no assessments.
- **Marker panels are proxies.** Expression of OCT4/POU5F1, NANOG or SOX2 is a correlate of a
  pluripotent state, not a definition of one. Thresholds are platform- and
  normalisation-dependent and do not transfer between datasets without recalibration.
- **A clean screen is not a negative result.** Absence of a flag means none of the configured
  criteria were breached. Risks that the criteria do not model are invisible to it.
- **False-negative rate is the number that matters.** D3.3 reports it explicitly on a public
  labelled benchmark. A screening criterion that never misses within its own benchmark is
  reported as *untested*, not as perfect.
- **Simulated trajectories are models.** Agreement between a simulated trajectory and a
  constraint says something about the model, not about a cell.

## If you are reviewing this repository

Treat any number produced here as a computational observation with the above caveats
attached. If you find this module cited anywhere as evidence of safety, that citation is
wrong, and we would like to know about it: research@syn.ai
