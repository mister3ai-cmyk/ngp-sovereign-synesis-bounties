import json
import pathlib
import datetime
import hashlib
from typing import Dict, Any


class ICHQ14AuditTrail:
    def __init__(self, log_path: str = "results/ich_q14_audit_log.jsonl"):
        self.log_path = pathlib.Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, actor: str, delta: str, operation_id: str, run_id: str = "", metadata: Dict[str, Any] | None = None):
        entry = {
            "actor": actor,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "delta": delta,
            "operation_id": operation_id,
            "run_id": run_id,
            "metadata": metadata or {},
            "hash": hashlib.sha256(
                f"{actor}:{datetime.datetime.utcnow().isoformat()}:{delta}:{operation_id}".encode()
            ).hexdigest(),
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def read_all(self) -> list:
        if not self.log_path.exists():
            return []
        with open(self.log_path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
