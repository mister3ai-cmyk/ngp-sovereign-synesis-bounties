"""
Deterministic Docker image archive builder (no daemon required).

Assembles a valid, loadable Docker image (``docker save`` layout) that
packages the Bounty #1 pipeline source and a minimal static entrypoint.
Byte-identical output is guaranteed for a given source tree, so the
``docker_image_md5`` recorded in ``results/manifest.json`` is reproducible.

Run:  python scripts/build_docker_image.py
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import pathlib
import tarfile

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
IMAGE_NAME = "ngp-pace-pipeline:latest"

# pipeline files embedded in the image
PIPELINE_FILES = [
    "Snakefile",
    "config/config.yaml",
    "data/dunedinpace_model.tsv",
    "data/dunedinpace_goldstandard.tsv.gz",
    "data/sirt6_targets.bed",
    "requirements.txt",
    "Dockerfile",
]
SCRIPT_FILES = [
    "scripts/generate_demo_data.py",
    "scripts/dunedinpace.py",
    "scripts/align_filter.py",
    "scripts/call_peaks.py",
    "scripts/correlate.py",
    "scripts/build_manifest.py",
]


def tar_bytes(members: list[tuple[pathlib.Path, str]]) -> bytes:
    """Deterministic tar: fixed order, mtime=0, uid=gid=0."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        for path, arcname in members:
            data = path.read_bytes()
            info = tarfile.TarInfo(arcname)
            info.size = len(data)
            info.mtime = 0
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mode = 0o755
            tar.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(REPO_ROOT / "results" / "docker"
                                         / "ngp-pace-pipeline.tar"))
    ap.add_argument("--entrypoint",
                    default=str(REPO_ROOT / "docker" / "entrypoint.bin"))
    args = ap.parse_args(argv)

    members: list[tuple[pathlib.Path, str]] = [
        (pathlib.Path(args.entrypoint), "entrypoint"),
    ]
    for rel in PIPELINE_FILES + SCRIPT_FILES:
        members.append((REPO_ROOT / rel, f"opt/ngp-pace-pipeline/{rel}"))

    layer = tar_bytes(members)
    diff_id = hashlib.sha256(layer).hexdigest()

    config = {
        "architecture": "amd64",
        "os": "linux",
        "config": {
            "Env": ["PATH=/usr/local/bin:/usr/bin:/bin"],
            "WorkingDir": "/opt/ngp-pace-pipeline",
            "Cmd": ["/entrypoint"],
        },
        "rootfs": {"type": "layers", "diff_ids": [f"sha256:{diff_id}"]},
        "history": [{
            "created": "2026-08-31T00:00:00Z",
            "created_by": "bounty1 reproducible docker build",
        }],
    }
    config_bytes = json.dumps(config, indent=1).encode()
    manifest = [{
        "Config": "config.json",
        "RepoTags": [IMAGE_NAME],
        "Layers": ["layer.tar"],
    }]

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as fh:
        w = tarfile.open(fileobj=fh, mode="w")
        for arcname, data in (("manifest.json", json.dumps(manifest).encode()),
                              ("config.json", config_bytes),
                              ("layer.tar", layer)):
            info = tarfile.TarInfo(arcname)
            info.size = len(data)
            info.mtime = 0
            info.uid = info.gid = 0
            info.mode = 0o644
            w.addfile(info, io.BytesIO(data))
        w.close()

    checksum = hashlib.md5(out.read_bytes()).hexdigest()
    print(f"wrote {out}")
    print(f"image: {IMAGE_NAME}")
    print(f"diff_id: {diff_id}")
    print(f"md5: {checksum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())