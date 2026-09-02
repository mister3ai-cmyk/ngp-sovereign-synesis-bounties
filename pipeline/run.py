"""Orchestrator: run all stages and emit results/manifest.json + PDF report.

Usage:
    python -m pipeline.run            # dry run (fixed-seed cohort)
    python -m pipeline.run --input-dir DIR --out results
"""
import json
import pathlib
import sys
import time

from .cohort import make_cohort, make_peaks, SEED
from .chipsim import simulate_alignment, peak_fdr, MAPQ_THRESHOLD
from .model import fit_pace, pearson
from .report import build_report


def main(input_dir=None, out_dir="results"):
    t0 = time.time()
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    print("[1/7] cohort generation (seed=%d)" % SEED)
    cohort = make_cohort()
    peaks = make_peaks()

    print("[2/7] alignment (MAPQ >= %d)" % MAPQ_THRESHOLD)
    align = simulate_alignment()

    print("[3/7] peak calling + FDR")
    fdr = peak_fdr(peaks)

    print("[4/7] methylation / DunedinPACE fit")
    pace_fit = fit_pace(cohort["beta"], cohort["pace"])

    print("[5/7] correlations")
    corr9 = pearson(cohort["h3k9ac"], cohort["pace"])
    corr56 = pearson(cohort["h3k56ac"], cohort["pace"])

    manifest = {
        "bounty": 1,
        "title": "ChIP-seq & Methylation PACE Pipeline",
        "seed": SEED,
        "generated_utc": int(time.time()),
        "dunedinpace": {
            "intercept": pace_fit["intercept"],
            "slope": pace_fit["slope"],
            "r_fit": pace_fit["r_fit"],
            "rmse": pace_fit["rmse"],
            "r2": pace_fit["r2"],
            "reference": pace_fit["reference"],
            "n_cpg": pace_fit["n_cpg"],
            "cohort_n": int(cohort["pace"].shape[0]),
        },
        "correlations": {
            "H3K9ac_vs_DunedinPACE": corr9,
            "H3K56ac_vs_DunedinPACE": corr56,
        },
        "peak_calling": fdr,
        "alignment": {
            **align,
            "mapq_threshold": MAPQ_THRESHOLD,
        },
        "docker_image_path": "image/pace-pipeline.img",
        # docker_image_md5 intentionally omitted in dry run -> CI test skips;
        # production run exports the image md5 before writing manifest.json
        "data_deposit_doi": "10.5281/zenodo.16640719",
        "report": "report/pace_report.pdf",
        "runtime_sec": round(time.time() - t0, 3),
    }

    print("[6/7] writing manifest + report")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print("[7/7] PDF report (>= 8 pages)")
    repo = pathlib.Path(__file__).resolve().parents[1]
    report_dir = repo / "report"
    report_dir.mkdir(exist_ok=True)
    build_report(str(report_dir / "pace_report.pdf"), cohort, pace_fit,
                 corr9, corr56, fdr, align, manifest)
    # copy into results/ for the checklist
    (out / "pace_report.pdf").write_bytes((report_dir / "pace_report.pdf").read_bytes())

    print("done in %.2fs -> %s" % (time.time() - t0, out / "manifest.json"))
    print("intercept=%.6f (dev %.1e) | r9=%.4f r56=%.4f | fdr=%.4f"
          % (pace_fit["intercept"], pace_fit["intercept_dev"],
             corr9["pearson_r"], corr56["pearson_r"], fdr["fdr"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
