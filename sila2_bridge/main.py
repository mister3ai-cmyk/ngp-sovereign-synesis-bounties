"""Main entrypoint for SiLA 2 Hamilton STARlet & DryLab4 Server."""
import time
import signal
import sys
import pathlib

# Ensure repo root is on python path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from sila2_bridge.server.grpc_server import create_grpc_server


def main():
    port = 50052
    audit_log = "results/ich_q14_audit_log.jsonl"
    server = create_grpc_server(port=port, audit_log_path=audit_log)
    server.start()
    print(f"[SiLA 2] Hamilton STARlet & DryLab4 Robotic Bridge Server listening on port {port}")

    def handle_shutdown(signum, frame):
        print("\n[SiLA 2] Gracefully shutting down...")
        server.stop(2)
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    server.wait_for_termination()


if __name__ == "__main__":
    main()
