# Vector Service Proto Files

This directory contains the Protocol Buffer definitions for the Vector Database Service, organized by domain following the PaymentProcessing service pattern.

## Structure

```
Protos/
├── Core/                           # Domain-specific proto files
│   ├── collections_messages.proto  # Collection operation messages
│   ├── collections_service.proto    # Collection service definition
│   ├── documents_messages.proto    # Document/vector operation messages
│   ├── documents_service.proto      # Document service definition
│   ├── search_messages.proto        # Search operation messages
│   ├── search_service.proto         # Search service definition
│   ├── health_messages.proto       # Health check messages
│   └── health_service.proto         # Health service definition
└── vector_service.proto            # Main service (composes all domains)
```

## Domain Organization

### Collections
- **Messages**: Collection CRUD operations (Create, List, Get, Delete)
- **Service**: `CollectionService` with collection management RPCs

### Documents
- **Messages**: Document/vector CRUD operations (Insert, Get, Update, Delete, Batch)
- **Service**: `DocumentService` with document management RPCs

### Search
- **Messages**: Semantic search operations (Search, Stream)
- **Service**: `SearchService` with search functionality RPCs

### Health
- **Messages**: Health check operations
- **Service**: `HealthService` with health monitoring RPCs

## Main Service

The `vector_service.proto` file imports all domain services and composes them into a single unified `VectorService` that provides all functionality through a single gRPC endpoint.

## Code Generation

Use the provided scripts to generate Python code:

- **Windows**: `scripts/generate_proto.bat`
- **Linux/macOS**: `scripts/generate_proto.sh`

The scripts will generate:
- `Core/*_pb2.py` - Message classes
- `Core/*_pb2_grpc.py` - Service classes
- `vector_service_pb2.py` - Main service messages
- `vector_service_pb2_grpc.py` - Main service classes

## Benefits

- **Maintainability**: Each domain can be maintained independently
- **Clean Imports**: Services only import the messages they need
- **Domain Separation**: Aligns with API Gateway organization
- **Future Scalability**: Easy to add new domains without bloating existing files
- **Consistent Pattern**: Follows the same organization as PaymentProcessing service
