.PHONY: proto test

proto:
	python -m grpc_tools.protoc -I./proto --python_out=./src/sila2_hamilton_bridge --grpc_python_out=./src/sila2_hamilton_bridge ./proto/sila2_hamilton_starlet.proto
	sed -i -e 's/import sila2_hamilton_starlet_pb2 as sila2__hamilton__starlet__pb2/from . import sila2_hamilton_starlet_pb2 as sila2__hamilton__starlet__pb2/g' ./src/sila2_hamilton_bridge/sila2_hamilton_starlet_pb2_grpc.py

test: proto
	pytest tests/test_bounty3_sila2.py -v