"""Deterministic end-to-end mock integration for Bounty #3.

Starts the gRPC server, executes RPCs against it, and validates responses.
"""
import sys
import time
import grpc

# Ensure src is importable
sys.path.insert(0, "src")
from sila2_bridge.server import serve
from sila2_bridge.audit_trail import ICHQ14AuditTrail

# Clean previous audit log for determinism
ICHQ14AuditTrail().log_path.unlink(missing_ok=True)

server = serve(port=50051)
time.sleep(0.5)

try:
    channel = grpc.insecure_channel("localhost:50051")
    stub = __import__("sila2_bridge.hamilton_starlet_pb2_grpc", fromlist=["HamiltonMicrolabSTARletStub"]).HamiltonMicrolabSTARletStub(channel)

    # Feature info
    info = stub.GetFeatureInfo(__import__("sila2_bridge.hamilton_starlet_pb2", fromlist=["GetFeatureInfoRequest"]).GetFeatureInfoRequest())
    assert info.vendor == "Hamilton"
    assert info.model == "Microlab STARlet"

    # Parameters
    params = stub.GetParameters(__import__("sila2_bridge.hamilton_starlet_pb2", fromlist=["GetParametersRequest"]).GetParametersRequest(parameter_set_id="default"))
    assert "flow_rate_ml_min" in params.parameters

    # Execute
    exec_req = __import__("sila2_bridge.hamilton_starlet_pb2", fromlist=["ExecuteMethodRequest"]).ExecuteMethodRequest(method_id="HPLC_001", parameters={})
    exec_resp = stub.ExecuteMethod(exec_req)
    assert exec_resp.status == "queued"
    run_id = exec_resp.run_id

    # Status
    status = stub.GetStatus(__import__("sila2_bridge.hamilton_starlet_pb2", fromlist=["GetStatusRequest"]).GetStatusRequest(run_id=run_id))
    assert status.progress_percent == 100

    # Audit trail
    audit_entries = list(stub.GetAuditTrail(__import__("sila2_bridge.hamilton_starlet_pb2", fromlist=["GetAuditTrailRequest"]).GetAuditTrailRequest(run_id=run_id)))
    assert len(audit_entries) >= 1

    print("E2E mock integration passed")
finally:
    server.stop(0)
