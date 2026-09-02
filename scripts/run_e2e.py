#!/usr/bin/env python3
"""End-to-end Integration Test for DryLab4 & SiLA 2 Robotic Bridge."""
import sys
import json
import pathlib
import time
import grpc

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import sila2_hamilton_starlet_pb2 as pb2
import sila2_hamilton_starlet_pb2_grpc as pb2_grpc

from sila2_bridge.server.grpc_server import create_grpc_server
from sila2_bridge.audit.ich_q14_audit import ICHQ14AuditTrail


def run_e2e():
    print("[E2E] Starting SiLA 2 DryLab4 Robotic Bridge End-to-End Test...")
    port = 50053
    audit_log = "results/ich_q14_e2e_audit.jsonl"
    if pathlib.Path(audit_log).exists():
        pathlib.Path(audit_log).unlink()

    server = create_grpc_server(port=port, audit_log_path=audit_log)
    server.start()
    print(f"[E2E] Test gRPC Server running on port {port}")

    try:
        channel = grpc.insecure_channel(f'localhost:{port}')
        stub = pb2_grpc.HamiltonSTARletFeatureStub(channel)

        # 1. Check Instrument Status & Clock Sync
        stat = stub.GetStatus(pb2.GetStatusRequest(actor="E2E_RUNNER"))
        assert stat.clock_sync_status == "LOCKED_432HZ_PTP", f"Unexpected clock status: {stat.clock_sync_status}"
        print(f"[E2E] Instrument Status verified: {stat.state}, Clock: {stat.clock_sync_status}")

        # 2. Check 432 Hz Clock Telemetry
        clock_stat = stub.GetMasterClockSync(pb2.GetMasterClockSyncRequest(actor="E2E_RUNNER"))
        assert clock_stat.frequency_hz == 432.0, f"Expected 432 Hz, got {clock_stat.frequency_hz}"
        assert clock_stat.utc_offset_ms < 1.0, f"PTP offset {clock_stat.utc_offset_ms} >= 1.0 ms"
        print(f"[E2E] 432 Hz Master Clock verified: Freq = {clock_stat.frequency_hz} Hz, Offset = {clock_stat.utc_offset_ms:.4f} ms")

        # 3. DryLab4 Retention-Time Prediction
        pred_resp = stub.PredictRetentionTimes(pb2.PredictRetentionTimesRequest(
            method_parameters_json=json.dumps({"tG_min": 15.0, "temperature_c": 35.0, "pH": 3.0}),
            actor="E2E_RUNNER",
            operation_id="E2E_OP_PRED_001"
        ))
        assert pred_resp.success, "PredictRetentionTimes failed"
        predictions = json.loads(pred_resp.prediction_results_json)
        assert len(predictions) >= 10, f"Expected >= 10 predictions, got {len(predictions)}"
        for p in predictions:
            err = p.get("error_fraction", abs(p["predicted_min"] - p["reference_min"]) / p["reference_min"])
            assert err <= 0.02, f"Error {err:.2%} > 2% for {p['compound']}"
        print(f"[E2E] DryLab4 RT Prediction verified: {len(predictions)} compounds within < 2% error")

        # 4. Hamilton STARlet Deck Initialization
        init_resp = stub.InitializeDeck(pb2.InitializeDeckRequest(
            deck_layout="Standard_Analytical_HPLC_Prep",
            actor="E2E_RUNNER",
            operation_id="E2E_OP_INIT_001"
        ))
        assert init_resp.success, "InitializeDeck failed"
        print(f"[E2E] STARlet Deck Initialization verified: {init_resp.status}")

        # 5. Automated Sample Preparation Sequence
        prep_resp = stub.PrepareDryLabSequence(pb2.PrepareDryLabSequenceRequest(
            sequence_configuration_json="",
            actor="E2E_RUNNER",
            operation_id="E2E_OP_PREP_001"
        ))
        assert prep_resp.success, "PrepareDryLabSequence failed"
        assert prep_resp.prepared_vials_count == 10, f"Expected 10 vials, got {prep_resp.prepared_vials_count}"
        print(f"[E2E] Sample Preparation verified: {prep_resp.prepared_vials_count} vials prepared")

        # 6. Trigger HPLC Run
        hplc_resp = stub.TriggerHPLCRun(pb2.TriggerHPLCRunRequest(
            vial_position="RACK_1_POS_01",
            injection_volume_ul=10.0,
            actor="E2E_RUNNER",
            operation_id="E2E_OP_HPLC_001"
        ))
        assert hplc_resp.success, "TriggerHPLCRun failed"
        run_id = hplc_resp.run_id
        print(f"[E2E] HPLC Run Triggered: {run_id}")

        # 7. Acquire Waters Empower CDS Data
        empower_resp = stub.AcquireCDSData(pb2.AcquireCDSDataRequest(
            run_id=run_id,
            cds_source="Waters_Empower",
            actor="E2E_RUNNER",
            operation_id="E2E_OP_CDS_001"
        ))
        assert empower_resp.success, "AcquireCDSData (Empower) failed"
        empower_data = json.loads(empower_resp.cds_results_json)
        assert len(empower_data["peaks"]) == 10, f"Expected 10 peaks, got {len(empower_data['peaks'])}"
        print(f"[E2E] Waters Empower CDS Data Acquired: {len(empower_data['peaks'])} peaks")

        # 8. Acquire Agilent OpenLab CDS Data
        openlab_resp = stub.AcquireCDSData(pb2.AcquireCDSDataRequest(
            run_id=run_id,
            cds_source="Agilent_OpenLab",
            actor="E2E_RUNNER",
            operation_id="E2E_OP_CDS_002"
        ))
        assert openlab_resp.success, "AcquireCDSData (OpenLab) failed"
        openlab_data = json.loads(openlab_resp.cds_results_json)
        assert len(openlab_data["peaks"]) == 10, f"Expected 10 peaks, got {len(openlab_data['peaks'])}"
        print(f"[E2E] Agilent OpenLab CDS Data Acquired: {len(openlab_data['peaks'])} peaks")

        # 9. Verify ICH Q14 Audit Trail
        audit_trail = ICHQ14AuditTrail(log_path=audit_log)
        entries = audit_trail.read_all_entries()
        assert len(entries) >= 6, f"Expected >= 6 audit entries, got {len(entries)}"
        for e in entries:
            missing = {"actor", "timestamp", "delta", "operation_id"} - set(e.keys())
            assert not missing, f"Missing ICH Q14 fields: {missing}"
        assert audit_trail.verify_audit_integrity(), "Audit hash chain verification failed"
        print(f"[E2E] ICH Q14 Immutable Audit Trail verified: {len(entries)} entries, SHA-256 chain intact")

        print("[E2E] ALL END-TO-END INTEGRATION TESTS PASSED SUCCESSFULLY!")
        return 0
    finally:
        server.stop(0)


if __name__ == "__main__":
    sys.exit(run_e2e())
