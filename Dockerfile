FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY src/ ./src/
COPY tests/ ./tests/
COPY results/ ./results/
COPY proto/ ./proto/
COPY schemas/ ./schemas/

EXPOSE 50051

CMD ["python", "-m", "sila2_bridge.server"]
