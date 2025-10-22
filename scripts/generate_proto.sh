#!/bin/bash
# Generate Python code from Protocol Buffer definitions
# Now generates from vector-db-contracts (single source of truth)

cd "$(dirname "$0")/.."

echo "Generating Python code from .proto files..."
echo "Source: vector-db-contracts/src/VectorDB.Contracts/Protos/"
echo ""

# Define paths
PROTO_DIR="vector-db-contracts/src/VectorDB.Contracts/Protos"
OUTPUT_DIR="src/service/protos"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR/Core"

# Generate code for all Core proto files
python -m grpc_tools.protoc \
  -I./$PROTO_DIR \
  --python_out=./$OUTPUT_DIR \
  --grpc_python_out=./$OUTPUT_DIR \
  ./$PROTO_DIR/Core/collections_messages.proto

python -m grpc_tools.protoc \
  -I./$PROTO_DIR \
  --python_out=./$OUTPUT_DIR \
  --grpc_python_out=./$OUTPUT_DIR \
  ./$PROTO_DIR/Core/collections_service.proto

python -m grpc_tools.protoc \
  -I./$PROTO_DIR \
  --python_out=./$OUTPUT_DIR \
  --grpc_python_out=./$OUTPUT_DIR \
  ./$PROTO_DIR/Core/documents_messages.proto

python -m grpc_tools.protoc \
  -I./$PROTO_DIR \
  --python_out=./$OUTPUT_DIR \
  --grpc_python_out=./$OUTPUT_DIR \
  ./$PROTO_DIR/Core/documents_service.proto

python -m grpc_tools.protoc \
  -I./$PROTO_DIR \
  --python_out=./$OUTPUT_DIR \
  --grpc_python_out=./$OUTPUT_DIR \
  ./$PROTO_DIR/Core/search_messages.proto

python -m grpc_tools.protoc \
  -I./$PROTO_DIR \
  --python_out=./$OUTPUT_DIR \
  --grpc_python_out=./$OUTPUT_DIR \
  ./$PROTO_DIR/Core/search_service.proto

python -m grpc_tools.protoc \
  -I./$PROTO_DIR \
  --python_out=./$OUTPUT_DIR \
  --grpc_python_out=./$OUTPUT_DIR \
  ./$PROTO_DIR/Core/health_messages.proto

python -m grpc_tools.protoc \
  -I./$PROTO_DIR \
  --python_out=./$OUTPUT_DIR \
  --grpc_python_out=./$OUTPUT_DIR \
  ./$PROTO_DIR/Core/health_service.proto

# Generate code for the main vector service
python -m grpc_tools.protoc \
  -I./$PROTO_DIR \
  --python_out=./$OUTPUT_DIR \
  --grpc_python_out=./$OUTPUT_DIR \
  ./$PROTO_DIR/vector_service.proto

if [ $? -eq 0 ]; then
    echo ""
    echo "Success! Generated files:"
    echo "  - src/service/protos/Core/*_pb2.py"
    echo "  - src/service/protos/Core/*_pb2_grpc.py"
    echo "  - src/service/protos/vector_service_pb2.py"
    echo "  - src/service/protos/vector_service_pb2_grpc.py"
    echo ""
    echo "Note: These are generated from vector-db-contracts (single source of truth)"
else
    echo ""
    echo "Error: Failed to generate proto files"
    echo "Make sure you have installed: pip install grpcio-tools"
    exit 1
fi
