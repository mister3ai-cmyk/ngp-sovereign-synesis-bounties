# Sovereign Synesis — Bounty #1 pipeline image
# Wraps the identical pipeline stages in a reproducible container.
FROM python:3.11-slim

WORKDIR /srv/pace
COPY pipeline/ ./pipeline/
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# production entrypoint: stages 1-7 over mounted FASTQ + methylation inputs
CMD ["python", "-m", "pipeline.run", "--input-dir", "/srv/inputs", "--out", "results"]
