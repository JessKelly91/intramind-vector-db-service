#!/bin/bash
# Generate Python code from Protocol Buffer definitions

cd "$(dirname "$0")/.."

echo "Generating Python code from .proto files..."

# Generate code for all Core proto files
python -m grpc_tools.protoc \
  -I./src/service/protos \
  --python_out=./src/service/protos \
  --grpc_python_out=./src/service/protos \
  ./src/service/protos/Core/collections_messages.proto

python -m grpc_tools.protoc \
  -I./src/service/protos \
  --python_out=./src/service/protos \
  --grpc_python_out=./src/service/protos \
  ./src/service/protos/Core/collections_service.proto

python -m grpc_tools.protoc \
  -I./src/service/protos \
  --python_out=./src/service/protos \
  --grpc_python_out=./src/service/protos \
  ./src/service/protos/Core/documents_messages.proto

python -m grpc_tools.protoc \
  -I./src/service/protos \
  --python_out=./src/service/protos \
  --grpc_python_out=./src/service/protos \
  ./src/service/protos/Core/documents_service.proto

python -m grpc_tools.protoc \
  -I./src/service/protos \
  --python_out=./src/service/protos \
  --grpc_python_out=./src/service/protos \
  ./src/service/protos/Core/search_messages.proto

python -m grpc_tools.protoc \
  -I./src/service/protos \
  --python_out=./src/service/protos \
  --grpc_python_out=./src/service/protos \
  ./src/service/protos/Core/search_service.proto

python -m grpc_tools.protoc \
  -I./src/service/protos \
  --python_out=./src/service/protos \
  --grpc_python_out=./src/service/protos \
  ./src/service/protos/Core/health_messages.proto

python -m grpc_tools.protoc \
  -I./src/service/protos \
  --python_out=./src/service/protos \
  --grpc_python_out=./src/service/protos \
  ./src/service/protos/Core/health_service.proto

# Generate code for the main vector service
python -m grpc_tools.protoc \
  -I./src/service/protos \
  --python_out=./src/service/protos \
  --grpc_python_out=./src/service/protos \
  ./src/service/protos/vector_service.proto

if [ $? -eq 0 ]; then
    echo ""
    echo "Success! Generated files:"
    echo "  - src/service/protos/Core/*_pb2.py"
    echo "  - src/service/protos/Core/*_pb2_grpc.py"
    echo "  - src/service/protos/vector_service_pb2.py"
    echo "  - src/service/protos/vector_service_pb2_grpc.py"
    echo ""
    echo "You can now use these in your Python code."
else
    echo ""
    echo "Error: Failed to generate proto files"
    echo "Make sure you have installed: pip install grpcio-tools"
    exit 1
fi
