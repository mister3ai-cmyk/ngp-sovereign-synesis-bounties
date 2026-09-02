FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY . .

# Expose SiLA 2 gRPC port
EXPOSE 50052

# Health check verifying gRPC server readiness
HEALTHCHECK --interval=2s --timeout=3s --start-period=3s --retries=3 \
    CMD python3 -c "import grpc, sila2_hamilton_starlet_pb2 as pb2, sila2_hamilton_starlet_pb2_grpc as pb2_grpc; channel = grpc.insecure_channel('localhost:50052'); stub = pb2_grpc.HamiltonSTARletFeatureStub(channel); res = stub.GetStatus(pb2.GetStatusRequest(actor='HEALTHCHECK'), timeout=2); assert res.state == 'IDLE'" || exit 1

CMD ["python3", "sila2_bridge/main.py"]
