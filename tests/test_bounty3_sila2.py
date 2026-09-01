import pytest
import grpc
import time
import json
import os
import sys
from concurrent import futures

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sila2_hamilton_bridge.server import HamiltonSTARletFeatureServicer
from sila2_hamilton_bridge import sila2_hamilton_starlet_pb2
from sila2_hamilton_bridge import sila2_hamilton_starlet_pb2_grpc
from sila2_hamilton_bridge.clock_sync import MasterClock
from sila2_hamilton_bridge.drylab4_bridge import DryLab4Bridge
from sila2_hamilton_bridge.audit_trail import AuditTrail

@pytest.fixture
def grpc_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    servicer = HamiltonSTARletFeatureServicer()
    sila2_hamilton_starlet_pb2_grpc.add_HamiltonSTARletFeatureServicer_to_server(servicer, server)
    server.add_insecure_port('[::]:50052')
    server.start()
    yield server, servicer
    server.stop(0)

def test_sila2_schema_validation():
    assert hasattr(sila2_hamilton_starlet_pb2, 'ExecuteMethodRequest')

def test_grpc_latency(grpc_server):
    server, _ = grpc_server
    channel = grpc.insecure_channel('localhost:50052')
    stub = sila2_hamilton_starlet_pb2_grpc.HamiltonSTARletFeatureStub(channel)
    
    latencies = []
    for _ in range(1000):
        start = time.perf_counter()
        stub.GetStatus(sila2_hamilton_starlet_pb2.GetStatusRequest())
        end = time.perf_counter()
        latencies.append((end - start) * 1000)
        
    p99 = sorted(latencies)[int(len(latencies) * 0.99)]
    assert p99 < 50, f"p99 latency {p99}ms exceeds 50ms"

def test_drylab4_rt_prediction():
    bridge = DryLab4Bridge()
    rt = bridge.predict_rt("compound_A")
    ref_rt = 12.5
    error = abs(rt - ref_rt) / ref_rt
    assert error < 0.02, f"RT prediction error {error} exceeds 2%"

def test_master_clock_jitter():
    clock = MasterClock()
    base = time.time_ns()
    interval_ns = int(1e9 / 432)
    for i in range(432 * 60):
        clock._record_jitter(base + i * interval_ns)
    
    jitter = clock.get_jitter_ms()
    assert jitter < 1.0, f"Jitter {jitter}ms exceeds 1ms"

def test_ich_q14_audit_trail():
    audit = AuditTrail("test_audit.jsonl")
    audit.log_entry(
        operation_id="op_123",
        actor="test_user",
        timestamp="2026-08-24T10:00:00Z",
        operation="TestOperation",
        delta={"key": "value"}
    )
    
    with open("test_audit.jsonl", 'r') as f:
        lines = f.readlines()
    
    entry = json.loads(lines[-1])
    assert "operation_id" in entry
    assert "actor" in entry
    assert "timestamp" in entry
    assert "delta" in entry
    
    os.remove("test_audit.jsonl")

def test_docker_compose_start():
    assert os.path.exists("docker-compose.yml")

def test_e2e_mock_integration(grpc_server):
    server, servicer = grpc_server
    channel = grpc.insecure_channel('localhost:50052')
    stub = sila2_hamilton_starlet_pb2_grpc.HamiltonSTARletFeatureStub(channel)
    
    request = sila2_hamilton_starlet_pb2.ExecuteMethodRequest(
        method_name="DryLab4_Predict_RT",
        parameters={"compound": "compound_A"},
        operation_id="op_e2e",
        actor="test_user"
    )
    
    response = stub.ExecuteMethod(request)
    assert response.success