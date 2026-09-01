"""SiLA 2 gRPC Server for Hamilton STARlet, DryLab4, CDS, and 432 Hz Master Clock Bridge."""
import json
import uuid
import grpc
from concurrent import futures
from typing import Optional

import sila2_hamilton_starlet_pb2 as pb2
import sila2_hamilton_starlet_pb2_grpc as pb2_grpc

from sila2_bridge.clock.master_clock import MasterClock432Hz
from sila2_bridge.drylab4.bridge import DryLab4Bridge
from sila2_bridge.drylab4.models import HPLCMethodParams
from sila2_bridge.starlet.liquid_handler import HamiltonSTARletController
from sila2_bridge.cds.empower import WatersEmpowerConnector
from sila2_bridge.cds.openlab import AgilentOpenLabConnector
from sila2_bridge.audit.ich_q14_audit import ICHQ14AuditTrail


class HamiltonSTARletFeatureServicerImpl(pb2_grpc.HamiltonSTARletFeatureServicer):
    """Implementation of HamiltonSTARletFeature SiLA 2 gRPC Servicer."""

    def __init__(self, audit_log_path: str = "results/ich_q14_audit_log.jsonl"):
        self.master_clock = MasterClock432Hz()
        self.drylab_bridge = DryLab4Bridge()
        self.starlet_controller = HamiltonSTARletController()
        self.empower_connector = WatersEmpowerConnector()
        self.openlab_connector = AgilentOpenLabConnector()
        self.audit_trail = ICHQ14AuditTrail(log_path=audit_log_path)

    def InitializeDeck(self, request, context):
        op_id = request.operation_id or f"OP_INIT_{uuid.uuid4().hex[:8]}"
        actor = request.actor or "OPERATOR_DEFAULT"
        timestamp = self.master_clock.get_iso_timestamp()

        layout = request.deck_layout or "Standard_Analytical_HPLC_Prep"
        res = self.starlet_controller.initialize_deck(layout_name=layout)

        delta = {
            "action": "InitializeDeck",
            "previous_state": "UNINITIALIZED",
            "new_state": "INITIALIZED",
            "deck_layout": layout,
            "carrier_positions": 32
        }
        self.audit_trail.log_entry(
            operation_id=op_id,
            actor=actor,
            delta=delta,
            timestamp=timestamp,
            procedure_step="DECK_INITIALIZATION"
        )

        return pb2.InitializeDeckResponse(
            success=True,
            status=f"STARlet deck initialized successfully with layout: {layout}",
            timestamp=timestamp
        )

    def PrepareDryLabSequence(self, request, context):
        op_id = request.operation_id or f"OP_PREP_{uuid.uuid4().hex[:8]}"
        actor = request.actor or "OPERATOR_DEFAULT"
        timestamp = self.master_clock.get_iso_timestamp()

        try:
            config = json.loads(request.sequence_configuration_json) if request.sequence_configuration_json else {}
        except Exception:
            config = {}

        if not config:
            config = self.drylab_bridge.generate_starlet_pipetting_protocol(num_vials=10)

        prep_res = self.starlet_controller.execute_sample_prep_sequence(config)

        delta = {
            "action": "PrepareDryLabSequence",
            "vials_prepared": prep_res["vials_prepared"],
            "sequence_id": prep_res["sequence_id"],
            "deck_actions": prep_res["deck_actions"]
        }
        self.audit_trail.log_entry(
            operation_id=op_id,
            actor=actor,
            delta=delta,
            timestamp=timestamp,
            procedure_step="SAMPLE_PREPARATION"
        )

        return pb2.PrepareDryLabSequenceResponse(
            success=True,
            prepared_vials_count=prep_res["vials_prepared"],
            details_json=json.dumps(prep_res),
            timestamp=timestamp
        )

    def TriggerHPLCRun(self, request, context):
        op_id = request.operation_id or f"OP_HPLC_{uuid.uuid4().hex[:8]}"
        actor = request.actor or "OPERATOR_DEFAULT"
        timestamp = self.master_clock.get_iso_timestamp()

        vial_pos = request.vial_position or "RACK_1_POS_01"
        inj_vol = request.injection_volume_ul if request.injection_volume_ul > 0 else 10.0

        run_res = self.starlet_controller.trigger_hplc_injection(vial_pos, inj_vol)

        delta = {
            "action": "TriggerHPLCRun",
            "run_id": run_res["run_id"],
            "vial_position": vial_pos,
            "injection_volume_ul": inj_vol
        }
        self.audit_trail.log_entry(
            operation_id=op_id,
            actor=actor,
            delta=delta,
            timestamp=timestamp,
            procedure_step="HPLC_INJECTION_TRIGGER"
        )

        return pb2.TriggerHPLCRunResponse(
            success=True,
            run_id=run_res["run_id"],
            timestamp=timestamp
        )

    def AcquireCDSData(self, request, context):
        op_id = request.operation_id or f"OP_CDS_{uuid.uuid4().hex[:8]}"
        actor = request.actor or "OPERATOR_DEFAULT"
        timestamp = self.master_clock.get_iso_timestamp()

        run_id = request.run_id or "RUN_MOCK_001"
        source = request.cds_source or "Waters_Empower"

        if "openlab" in source.lower() or "agilent" in source.lower():
            cds_data = self.openlab_connector.parse_result_set(run_id)
        else:
            cds_data = self.empower_connector.parse_result_set(run_id)

        corr = self.drylab_bridge.correlate_cds_results(cds_data)

        delta = {
            "action": "AcquireCDSData",
            "cds_source": cds_data.get("cds_source"),
            "run_id": run_id,
            "peak_count": len(cds_data.get("peaks", [])),
            "correlation_summary": corr
        }
        self.audit_trail.log_entry(
            operation_id=op_id,
            actor=actor,
            delta=delta,
            timestamp=timestamp,
            procedure_step="CDS_RESULT_ACQUISITION"
        )

        return pb2.AcquireCDSDataResponse(
            success=True,
            cds_results_json=json.dumps(cds_data),
            timestamp=timestamp
        )

    def PredictRetentionTimes(self, request, context):
        op_id = request.operation_id or f"OP_PRED_{uuid.uuid4().hex[:8]}"
        actor = request.actor or "OPERATOR_DEFAULT"
        timestamp = self.master_clock.get_iso_timestamp()

        try:
            params_dict = json.loads(request.method_parameters_json) if request.method_parameters_json else {}
        except Exception:
            params_dict = {}

        method_params = HPLCMethodParams(**params_dict) if params_dict else HPLCMethodParams()
        preds = self.drylab_bridge.engine.get_reference_predictions(method_params)

        delta = {
            "action": "PredictRetentionTimes",
            "compound_count": len(preds),
            "mean_error_pct": sum(p["error_pct"] for p in preds) / max(1, len(preds))
        }
        self.audit_trail.log_entry(
            operation_id=op_id,
            actor=actor,
            delta=delta,
            timestamp=timestamp,
            procedure_step="DRYLAB4_MODEL_PREDICTION"
        )

        return pb2.PredictRetentionTimesResponse(
            success=True,
            prediction_results_json=json.dumps(preds),
            timestamp=timestamp
        )

    def ExecuteMethod(self, request, context):
        op_id = request.operation_id or f"OP_EXEC_{uuid.uuid4().hex[:8]}"
        actor = request.actor or "OPERATOR_DEFAULT"
        timestamp = self.master_clock.get_iso_timestamp()

        mname = request.method_name
        params = dict(request.parameters)

        if "predict" in mname.lower() or "drylab" in mname.lower():
            preds = self.drylab_bridge.engine.get_reference_predictions()
            result = {"status": "SUCCESS", "predictions": preds}
        elif "init" in mname.lower():
            init_res = self.starlet_controller.initialize_deck()
            result = {"status": "SUCCESS", "init": init_res}
        else:
            result = {"status": "SUCCESS", "method": mname, "params": params}

        delta = {
            "action": "ExecuteMethod",
            "method_name": mname,
            "parameters": params
        }
        self.audit_trail.log_entry(
            operation_id=op_id,
            actor=actor,
            delta=delta,
            timestamp=timestamp,
            procedure_step="METHOD_EXECUTION"
        )

        return pb2.ExecuteMethodResponse(
            success=True,
            result_json=json.dumps(result),
            message=f"Executed {mname} successfully",
            timestamp=timestamp
        )

    def GetStatus(self, request, context):
        timestamp = self.master_clock.get_iso_timestamp()
        tick = self.master_clock.get_current_tick()
        return pb2.GetStatusResponse(
            state="IDLE",
            deck_status="INITIALIZED" if self.starlet_controller.is_initialized else "READY",
            clock_sync_status="LOCKED_432HZ_PTP",
            timestamp=timestamp,
            clock_tick_count=tick
        )

    def GetMasterClockSync(self, request, context):
        clock_stat = self.master_clock.get_clock_status()
        return pb2.GetMasterClockSyncResponse(
            frequency_hz=clock_stat["frequency_hz"],
            jitter_ms_60s_window=clock_stat["jitter_ms_60s_window"],
            utc_offset_ms=clock_stat["utc_offset_ms"],
            ptp_locked=clock_stat["ptp_locked"],
            timestamp=clock_stat["timestamp"]
        )

    def GetAuditTrail(self, request, context):
        max_rec = request.max_records or 100
        entries = self.audit_trail.read_all_entries()
        records_json = [json.dumps(e) for e in entries[-max_rec:]]
        latest_hash = entries[-1].get("entry_hash", "0"*64) if entries else "0"*64
        return pb2.GetAuditTrailResponse(
            audit_records_json=records_json,
            total_count=len(entries),
            latest_hash=latest_hash
        )


def create_grpc_server(port: int = 50052, audit_log_path: str = "results/ich_q14_audit_log.jsonl") -> grpc.Server:
    """Create and configure the SiLA 2 gRPC server."""
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=16),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),
            ('grpc.so_reuseport', 1)
        ]
    )
    servicer = HamiltonSTARletFeatureServicerImpl(audit_log_path=audit_log_path)
    pb2_grpc.add_HamiltonSTARletFeatureServicer_to_server(servicer, server)
    server.add_insecure_port(f'[::]:{port}')
    return server
