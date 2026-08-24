import json
import os
import datetime

class AuditTrail:
    def __init__(self, filename="audit_trail.jsonl"):
        self.filename = filename
        if not os.path.exists(self.filename):
            open(self.filename, 'w').close()

    def log_entry(self, operation_id, actor, timestamp, operation, delta):
        entry = {
            "operation_id": operation_id,
            "actor": actor,
            "timestamp": timestamp,
            "operation": operation,
            "delta": delta
        }
        with open(self.filename, 'a') as f:
            f.write(json.dumps(entry) + "\n")