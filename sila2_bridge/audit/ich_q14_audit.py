"""ICH Q14 Compliant Immutable Audit Trail Logger.

Adheres to ICH Q14 analytical procedure lifecycle management and 21 CFR Part 11
data integrity requirements. Generates append-only cryptographically chained JSONL logs.
Every entry strictly includes: 'actor', 'timestamp', 'delta', 'operation_id'.
"""
import os
import json
import hashlib
import pathlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


class ICHQ14AuditTrail:
    """Immutable, cryptographically chained audit logger for analytical procedure lifecycles."""

    REQUIRED_FIELDS = {"actor", "timestamp", "delta", "operation_id"}

    def __init__(self, log_path: str = "results/ich_q14_audit_log.jsonl"):
        self.log_path = pathlib.Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._last_hash = self._compute_initial_hash()

    def _compute_initial_hash(self) -> str:
        """Read existing log or initialize genesis hash."""
        if not self.log_path.exists() or self.log_path.stat().st_size == 0:
            return "0" * 64
        
        last_line = ""
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last_line = line.strip()
        if last_line:
            try:
                data = json.loads(last_line)
                return data.get("entry_hash", hashlib.sha256(last_line.encode("utf-8")).hexdigest())
            except Exception:
                pass
        return "0" * 64

    def log_entry(
        self,
        operation_id: str,
        actor: str,
        delta: Dict[str, Any],
        timestamp: Optional[str] = None,
        procedure_step: Optional[str] = None,
        method_operable_design_region: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record an immutable ICH Q14 compliant audit entry.
        
        Strictly guarantees the presence of:
        - actor
        - timestamp
        - delta
        - operation_id
        """
        if not timestamp:
            timestamp = datetime.now(timezone.utc).isoformat()

        entry: Dict[str, Any] = {
            "actor": actor,
            "timestamp": timestamp,
            "delta": delta,
            "operation_id": operation_id,
            "procedure_step": procedure_step or "ANALYTICAL_OPERATION",
            "prev_hash": self._last_hash,
            "ich_q14_category": "PARAMETER_LIFECYCLE_CHANGE"
        }
        
        if method_operable_design_region:
            entry["modr_state"] = method_operable_design_region

        # Compute SHA-256 digest of canonical JSON payload
        serialized = json.dumps(entry, sort_keys=True)
        entry_hash = hashlib.sha256(f"{self._last_hash}:{serialized}".encode("utf-8")).hexdigest()
        entry["entry_hash"] = entry_hash
        self._last_hash = entry_hash

        # Write to JSONL
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

        return entry

    def read_all_entries(self) -> List[Dict[str, Any]]:
        """Read and parse all audit trail records."""
        if not self.log_path.exists():
            return []
        entries = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line.strip()))
        return entries

    def verify_audit_integrity(self) -> bool:
        """Verify the cryptographic hash chain of the entire audit log."""
        entries = self.read_all_entries()
        if not entries:
            return True

        current_prev_hash = "0" * 64
        for i, entry in enumerate(entries):
            # Check required fields
            missing = self.REQUIRED_FIELDS - set(entry.keys())
            if missing:
                return False
            
            if entry.get("prev_hash") != current_prev_hash:
                return False
            
            entry_copy = dict(entry)
            stored_hash = entry_copy.pop("entry_hash", None)
            serialized = json.dumps(entry_copy, sort_keys=True)
            recomputed_hash = hashlib.sha256(f"{current_prev_hash}:{serialized}".encode("utf-8")).hexdigest()
            
            if stored_hash != recomputed_hash:
                return False
            
            current_prev_hash = stored_hash

        return True
