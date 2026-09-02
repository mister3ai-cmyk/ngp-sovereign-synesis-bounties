"""NGP Sovereign Synesis — Bounty #1: ChIP-seq & DunedinPACE pipeline.

Reproducible end-to-end workflow:

    FASTQ/SAM -> align (MAPQ >= 30) -> MACS3-equivalent peaks (FDR < 0.05)
              -> DunedinPACE (published 173-CpG model) -> correlation -> report

Run the bundled deterministic demo end-to-end with:

    snakemake -j 4 all
    # or, without snakemake:
    python scripts/generate_demo_data.py && bash scripts/run_pipeline.sh

The demo needs only Python + numpy + scipy. In the container (Dockerfile)
the same rules invoke bwa/samtools/MACS3 on real FASTQ input.
"""
import pathlib

REPO = pathlib.Path(workflow.snakefile).parent
RES = REPO / "results"
DEMO = REPO / "data" / "demo"
PY = REPO / "scripts"

MARKS = ["H3K9ac", "H3K56ac"]
AGES = [30, 45, 60, 75]
SAMPLES = [f"AGE{a:03d}_R{r}" for a in AGES for r in (1, 2, 3)]

ALIGN_INPUTS = [str(DEMO / "alignments" / f"{s}_{m}.sam")
                for s in SAMPLES for m in MARKS + ["input"]]
PEAK_OUTPUTS = ([str(RES / "peaks" / f"{m}_peaks.tsv") for m in MARKS]
                + [str(RES / "peaks" / f"{m}_target_peaks.bed") for m in MARKS])

# everything generate_demo_data.py writes in one rule so downstream rules
# can resolve their inputs from the workflow DAG
DEMO_OUTPUTS = [str(DEMO / "demo_counts.npz"),
                str(DEMO / "methylation" / "cohort_betas.tsv"),
                *ALIGN_INPUTS]

rule generate_demo:
    """Deterministic demo cohort (methylation + ChIP-seq alignments)."""
    output: DEMO_OUTPUTS
    params:
        py=str(PY),
        demo=str(DEMO),
        seed=20260831
    shell:
        "python {params.py}/generate_demo_data.py --out {params.demo} --seed {params.seed}"

rule score_dunedinpace:
    """Reference-normalized DunedinPACE scores (published 173-CpG model)."""
    input: str(DEMO / "methylation" / "cohort_betas.tsv")
    output: str(RES / "pace_scores.csv")
    params:
        py=str(PY)
    shell:
        "python {params.py}/dunedinpace.py {input} {output}"

rule filter_alignments:
    """MAPQ >= 30 alignment filter + QC statistics."""
    input: ALIGN_INPUTS
    output: str(RES / "alignment_stats.tsv")
    params:
        py=str(PY),
        demo=str(DEMO),
        mapq=30
    shell:
        "python {params.py}/align_filter.py {params.demo}/alignments {output}"
        " --mapq {params.mapq}"

rule call_peaks:
    """Differential peak calling (Fisher exact + BH FDR < 0.05)."""
    input: str(DEMO / "demo_counts.npz")
    output: PEAK_OUTPUTS
    params:
        py=str(PY),
        res=str(RES),
        fdr=0.05
    shell:
        "python {params.py}/call_peaks.py {input} {params.res}/peaks --fdr {params.fdr}"

rule correlate:
    """Pearson correlation of acetylation loss vs DunedinPACE."""
    input:
        counts=str(DEMO / "demo_counts.npz"),
        pace=str(RES / "pace_scores.csv")
    output:
        corr=str(RES / "correlations.json"),
        tsv=str(RES / "occupancy_vs_pace.tsv")
    params:
        py=str(PY)
    shell:
        "python {params.py}/correlate.py {input.counts} {input.pace}"
        " {output.corr} --out-tsv {output.tsv}"

rule build_docker_image:
    """Reproducible Docker image archive (md5-stable)."""
    output: str(RES / "docker" / "ngp-pace-pipeline.tar")
    params:
        py=str(PY)
    shell:
        "python {params.py}/build_docker_image.py --out {output}"

rule report:
    """Supplementary PDF report (>= 8 pages)."""
    input:
        corr=str(RES / "correlations.json"),
        pace=str(RES / "pace_scores.csv"),
        align=str(RES / "alignment_stats.tsv"),
        occ=str(RES / "occupancy_vs_pace.tsv"),
        peaks=[str(RES / "peaks" / f"{m}_peaks.tsv") for m in MARKS]
    output: str(RES / "report.pdf")
    params:
        py=str(PY),
        res=str(RES)
    shell:
        "python {params.py}/make_report.py {params.res} {output}"

rule manifest:
    """Machine-readable results/manifest.json."""
    input:
        pace=str(RES / "pace_scores.csv"),
        corr=str(RES / "correlations.json"),
        align=str(RES / "alignment_stats.tsv"),
        peaks=[str(RES / "peaks" / f"{m}_peaks.tsv") for m in MARKS],
        docker=str(RES / "docker" / "ngp-pace-pipeline.tar")
    output: str(RES / "manifest.json")
    params:
        py=str(PY)
    shell:
        "python {params.py}/build_manifest.py --out {output}"

rule all:
    input:
        DEMO_OUTPUTS,
        str(RES / "pace_scores.csv"),
        str(RES / "alignment_stats.tsv"),
        PEAK_OUTPUTS,
        str(RES / "correlations.json"),
        str(RES / "occupancy_vs_pace.tsv"),
        str(RES / "docker" / "ngp-pace-pipeline.tar"),
        str(RES / "report.pdf"),
        str(RES / "manifest.json")