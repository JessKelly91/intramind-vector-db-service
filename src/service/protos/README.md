# Generated Protocol Buffer Files

This directory contains **generated Python code only**. Do not edit these files manually.

## Source of Truth

The source `.proto` files are maintained in:
```
vector-db-service/vector-db-contracts/src/VectorDB.Contracts/Protos/
```

## Generating Python Code

To regenerate the Python protobuf files from the contracts, run:

**Windows:**
```bash
scripts\generate_proto.bat
```

**Linux/macOS:**
```bash
scripts/generate_proto.sh
```

This will generate:
- `*_pb2.py` - Message classes
- `*_pb2_grpc.py` - Service stubs and servicers

## Directory Structure

```
protos/
├── __init__.py                    # Python package marker
├── Core/                          # Generated domain modules
│   ├── collections_*_pb2.py
│   ├── documents_*_pb2.py
│   ├── search_*_pb2.py
│   └── health_*_pb2.py
└── vector_service_pb2*.py         # Main service module
```

## Note

Generated files are gitignored (see `../.gitignore`). They must be regenerated after:
- Pulling changes that modify `.proto` files
- Initial project setup
- Before running the service

