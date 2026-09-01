"""Unit test suite for SiLA 2 DryLab4 & Hamilton STARlet Robotic Bridge."""
import os
import json
import pytest
import numpy as np

from sila2_bridge.clock.master_clock import MasterClock432Hz
from sila2_bridge.drylab4.models import DryLab4Engine, HPLCMethodParams, REFERENCE_COMPOUNDS
from sila2_bridge.drylab4.bridge import DryLab4Bridge
from sila2_bridge.starlet.liquid_handler import HamiltonSTARletController
from sila2_bridge.cds.empower import WatersEmpowerConnector
from sila2_bridge.cds.openlab import AgilentOpenLabConnector
from sila2_bridge.audit.ich_q14_audit import ICHQ14AuditTrail


def test_master_clock_frequency_and_jitter():
    clock = MasterClock432Hz()
    assert clock.frequency_hz == 432.0
    assert abs(clock.nominal_period_sec - 1.0 / 432.0) < 1e-9

    metrics = clock.simulate_clock_window(duration_sec=60.0, simulated_jitter_std_dev_us=15.0)
    assert metrics["total_ticks"] == 25920
    assert metrics["jitter_ms_60s_window"] < 1.0
    assert metrics["utc_offset_ms"] < 1.0
    assert metrics["ptp_locked"] is True


def test_drylab4_lss_retention_modeling():
    engine = DryLab4Engine()
    method = HPLCMethodParams(tG_min=15.0, temperature_c=35.0, pH=3.0)
    predictions = engine.get_reference_predictions(method)
    
    assert len(predictions) == 10
    for p in predictions:
        assert p["error_fraction"] < 0.02, f"Error {p['error_fraction']} exceeds 2% for {p['compound']}"
        assert p["predicted_min"] > 0.0
        assert p["reference_min"] > 0.0


def test_drylab4_bridge_optimization_and_prep_protocol():
    bridge = DryLab4Bridge()
    space = bridge.optimize_method_design_space()
    assert "critical_pair" in space
    assert space["critical_resolution"] > 1.5
    assert space["meets_target"] is True

    protocol = bridge.generate_starlet_pipetting_protocol(num_vials=8)
    assert len(protocol["vials"]) == 8
    assert protocol["tip_type"] == "CO_RE_1000uL"


def test_hamilton_starlet_controller():
    controller = HamiltonSTARletController()
    init_res = controller.initialize_deck("Analytical_Prep_Grid")
    assert init_res["status"] == "INITIALIZED"
    assert controller.is_initialized is True

    prep_res = controller.execute_sample_prep_sequence({
        "vials": [
            {"tray_position": "RACK_1_POS_01", "sample_volume_ul": 250.0, "internal_std_volume_ul": 25.0, "diluent_volume_ul": 725.0},
            {"tray_position": "RACK_1_POS_02", "sample_volume_ul": 250.0, "internal_std_volume_ul": 25.0, "diluent_volume_ul": 725.0}
        ]
    })
    assert prep_res["vials_prepared"] == 2
    assert controller.vial_racks["RACK_1_POS_01"]["occupied"] is True
    assert controller.vial_racks["RACK_1_POS_01"]["volume_ul"] == 1000.0

    inj_res = controller.trigger_hplc_injection("RACK_1_POS_01", 15.0)
    assert "HPLC_RUN_" in inj_res["run_id"]
    assert inj_res["injection_volume_ul"] == 15.0


def test_cds_connectors():
    empower = WatersEmpowerConnector()
    emp_ss = empower.generate_sample_set([{"tray_position": "1:A1"}])
    assert len(emp_ss["lines"]) == 1
    emp_res = empower.parse_result_set("RUN_TEST_001")
    assert len(emp_res["peaks"]) == 10
    assert emp_res["system_suitability_passed"] is True

    openlab = AgilentOpenLabConnector()
    ag_seq = openlab.generate_sequence([{"tray_position": "P1-A1"}])
    assert len(ag_seq["lines"]) == 1
    ag_res = openlab.parse_result_set("RUN_TEST_002")
    assert len(ag_res["peaks"]) == 10
    assert ag_res["system_suitability_passed"] is True


def test_ich_q14_audit_logger(tmp_path):
    log_file = tmp_path / "test_audit.jsonl"
    audit = ICHQ14AuditTrail(log_path=str(log_file))
    
    e1 = audit.log_entry(operation_id="OP_1", actor="USER_A", delta={"step": "1"})
    e2 = audit.log_entry(operation_id="OP_2", actor="USER_B", delta={"step": "2"})
    
    for entry in [e1, e2]:
        assert "actor" in entry
        assert "timestamp" in entry
        assert "delta" in entry
        assert "operation_id" in entry
        assert "entry_hash" in entry

    assert audit.verify_audit_integrity() is True

    # Check tamper detection
    with open(log_file, "r") as f:
        lines = f.readlines()
    tampered_entry = json.loads(lines[0])
    tampered_entry["actor"] = "MALICIOUS_ACTOR"
    lines[0] = json.dumps(tampered_entry) + "\n"
    with open(log_file, "w") as f:
        f.writelines(lines)
    
    assert audit.verify_audit_integrity() is False
