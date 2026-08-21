import grpc
import threading
import time
from concurrent import futures
from typing import Dict, Any

from . import hamilton_starlet_pb2 as pb
from . import hamilton_starlet_pb2_grpc as pb_grpc

from .audit_trail import ICHQ14AuditTrail
from .drylab4_predictor import DryLab4RetentionPredictor
from .master_clock import MasterClock

audit = ICHQ14AuditTrail()
predictor = DryLab4RetentionPredictor()
clock = MasterClock()


class HamiltonMicrolabSTARletServicer(pb_grpc.HamiltonMicrolabSTARletServicer):
    def GetFeatureInfo(self, request, context):
        audit.log(actor="system", delta="GetFeatureInfo", operation_id="feat-info-1", metadata={})
        return pb.GetFeatureInfoResponse(
            feature_id="si.feature.hamilton.starlet",
            feature_version="1.0.0",
            vendor="Hamilton",
            model="Microlab STARlet",
            serial_number="MOCK-0001",
        )

    def GetParameters(self, request, context):
        audit.log(actor="system", delta=f"GetParameters:{request.parameter_set_id}", operation_id="get-param-1")
        return pb.GetParametersResponse(parameters={"flow_rate_ml_min": "1.0", "injection_vol_ul": "10"})

    def SetParameters(self, request, context):
        audit.log(actor="system", delta=f"SetParameters:{request.parameter_set_id}", operation_id="set-param-1")
        return pb.SetParametersResponse(success=True, message="Parameters updated")

    def ExecuteMethod(self, request, context):
        run_id = f"run-{int(time.time()*1000)}"
        audit.log(actor="system", delta=f"ExecuteMethod:{request.method_id}", operation_id="exec-method-1", run_id=run_id)
        return pb.ExecuteMethodResponse(run_id=run_id, status="queued", estimated_completion_utc="2025-01-01T00:00:00Z")

    def GetStatus(self, request, context):
        return pb.GetStatusResponse(run_id=request.run_id, status="completed", progress_percent=100, current_step="finished")

    def GetAuditTrail(self, request, context):
        for entry in audit.read_all():
            yield pb.AuditTrailEntry(
                operation_id=entry["operation_id"],
                actor=entry["actor"],
                timestamp=entry["timestamp"],
                delta=entry["delta"],
                run_id=entry.get("run_id", ""),
                metadata=entry.get("metadata", {}),
            )


def serve(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb_grpc.add_HamiltonMicrolabSTARletServicer_to_server(HamiltonMicrolabSTARletServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    return server


if __name__ == "__main__":
    srv = serve()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        srv.stop(0)
