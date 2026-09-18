import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json

from services.bridge_service import (
    DryLab4RetentionModel,
    ICHQ14AuditTrail,
    PTPMasterClock,
)


def test_ptp_clock_frequency_and_jitter():
    clock = PTPMasterClock(frequency_hz=432.0)
    assert clock.frequency_hz == 432.0
    ts = clock.get_timestamp()
    assert "iso_timestamp" in ts
    assert ts["jitter_ms"] < 1.0
    assert ts["utc_offset_ms"] < 1.0


def test_ich_q14_audit_trail_logging(tmp_path):
    log_file = tmp_path / "test_audit.jsonl"
    audit = ICHQ14AuditTrail(str(log_file))
    entry = audit.record_entry("analyst_1", "OP-9921", {"step": "dispense", "vol_ul": 10.0})
    assert entry["actor"] == "analyst_1"
    assert entry["operation_id"] == "OP-9921"
    assert entry["delta"]["vol_ul"] == 10.0

    assert log_file.exists()
    with open(log_file) as f:
        lines = f.readlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["actor"] == "analyst_1"


def test_drylab4_retention_time_accuracy():
    model = DryLab4RetentionModel()
    predictions = model.predict_retention_times()
    assert len(predictions) == 6
    for p in predictions:
        assert p["error_fraction"] < 0.02
        assert abs(p["predicted_min"] - p["reference_min"]) / p["reference_min"] < 0.02
