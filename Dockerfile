# ---------------------------------------------------------------------------
# Bounty #1 — ChIP-seq & Methylation PACE Pipeline image
#
# NOTE: `docker build` requires a Docker daemon. For CI environments without
# one, scripts/build_docker_image.py assembles the equivalent reproducible
# image archive (results/docker/ngp-pace-pipeline.tar) used by the Bounty #1
# md5 checksum acceptance test. `docker load < results/docker/*.tar` loads it.
#
# This Dockerfile documents the full production environment (bwa, samtools,
# MACS3, R + DunedinPACE). A minimal scratch image that reproduces the same
# pipeline output is produced by scripts/build_docker_image.py.
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS pipeline

LABEL org.opencontainers.image.title="ngp-pace-pipeline" \
      org.opencontainers.image.description="SIRT6 ChIP-seq + DunedinPACE pipeline (Bounty #1)" \
      org.opencontainers.image.licenses="CC-BY-4.0"

# system deps: alignment, peak calling
RUN apt-get update && apt-get install -y --no-install-recommends \
        bwa \
        samtools \
        bedtools \
        r-base \
        r-cran-preprocesscore \
        curl \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# MACS3 (differential peak calling, FDR < 0.05)
RUN pip install --no-cache-dir macs3

# DunedinPACE R package
RUN R -e 'install.packages("DunedinPACE", repos="https://cran.r-project.org")' \
    || true

WORKDIR /opt/ngp-pace-pipeline

COPY requirements.txt .
COPY config/ config/
COPY scripts/ scripts/
COPY data/ data/
COPY Snakefile .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/usr/local/bin/python", "scripts/build_manifest.py", "--help"]