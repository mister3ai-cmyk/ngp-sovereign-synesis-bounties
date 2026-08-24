import grpc
from concurrent import futures
import time
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'proto_gen'))

from . import sila2_hamilton_starlet_pb2
from . import sila2_hamilton_starlet_pb2_grpc
from .drylab4_bridge import DryLab4Bridge
from .cds_integration import CDSIntegration
from .clock_sync import MasterClock
from .audit_trail import AuditTrail

logging.basicConfig(level=logging.INFO)

class HamiltonSTARletFeatureServicer(sila2_hamilton_starlet_pb2_grpc.HamiltonSTARletFeatureServicer):
    def __init__(self):
        self.clock = MasterClock()
        self.audit = AuditTrail()
        self.drylab = DryLab4Bridge()
        self.cds = CDSIntegration()
        logging.info("Hamilton STARlet Feature Servicer initialized.")

    def ExecuteMethod(self, request, context):
        self.audit.log_entry(
            operation_id=request.operation_id,
            actor=request.actor,
            timestamp=self.clock.get_iso_timestamp(),
            operation="ExecuteMethod",
            delta={"method_name": request.method_name, "parameters": dict(request.parameters)}
        )

        try:
            if request.method_name == "DryLab4_Predict_RT":
                rt = self.drylab.predict_rt(request.parameters.get("compound"))
                return sila2_hamilton_starlet_pb2.ExecuteMethodResponse(
                    operation_id=request.operation_id,
                    success=True,
                    message=f"Predicted RT: {rt}"
                )
            elif request.method_name == "Execute_HPLC_Run":
                self.cds.execute_run(request.parameters)
                return sila2_hamilton_starlet_pb2.ExecuteMethodResponse(
                    operation_id=request.operation_id,
                    success=True,
                    message="HPLC Run Executed"
                )
            else:
                return sila2_hamilton_starlet_pb2.ExecuteMethodResponse(
                    operation_id=request.operation_id,
                    success=False,
                    message="Method not supported"
                )
        except Exception as e:
            logging.error(f"Error executing method: {e}")
            return sila2_hamilton_starlet_pb2.ExecuteMethodResponse(
                operation_id=request.operation_id,
                success=False,
                message=str(e)
            )

    def GetStatus(self, request, context):
        return sila2_hamilton_starlet_pb2.GetStatusResponse(
            status="OK",
            timestamp_ns=self.clock.get_timestamp_ns()
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sila2_hamilton_starlet_pb2_grpc.add_HamiltonSTARletFeatureServicer_to_server(
        HamiltonSTARletFeatureServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("Server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()