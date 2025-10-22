# Vector Service Protocol Buffer Definitions

This directory contains the **source Protocol Buffer definitions** for the Vector Database Service. These are the single source of truth for both C# and Python implementations.

## Directory Structure

```
Protos/
├── Core/                              # Domain-specific proto files
│   ├── collections_messages.proto     # Collection operation messages
│   ├── collections_service.proto      # Collection service definition
│   ├── documents_messages.proto       # Document/vector operation messages
│   ├── documents_service.proto        # Document service definition
│   ├── search_messages.proto          # Search operation messages
│   ├── search_service.proto           # Search service definition
│   ├── health_messages.proto          # Health check messages
│   └── health_service.proto           # Health service definition
└── vector_service.proto               # Main service (composes all domains)
```

## Domain Organization

### Collections Domain
- **Messages**: Collection CRUD operations (Create, List, Get, Delete)
- **Service**: `CollectionService` with collection management RPCs
- **Package**: `vectordb.core.v1`
- **C# Namespace**: `VectorDB.Contracts.Core.V1`

### Documents Domain
- **Messages**: Document/vector CRUD operations (Insert, Get, Update, Delete, Batch)
- **Service**: `DocumentService` with document management RPCs
- **Package**: `vectordb.core.v1`
- **C# Namespace**: `VectorDB.Contracts.Core.V1`

### Search Domain
- **Messages**: Semantic search operations (Search, Stream)
- **Service**: `SearchService` with search functionality RPCs
- **Package**: `vectordb.core.v1`
- **C# Namespace**: `VectorDB.Contracts.Core.V1`

### Health Domain
- **Messages**: Health check operations
- **Service**: `HealthService` with health monitoring RPCs
- **Package**: `vectordb.core.v1`
- **C# Namespace**: `VectorDB.Contracts.Core.V1`

## Main Service

The `vector_service.proto` file imports all domain services and composes them into a single unified `VectorService` that provides all functionality through one gRPC endpoint.

**Package**: `vectordb`  
**C# Namespace**: `VectorService`

## Code Generation

### C# / .NET

The `VectorDB.Contracts.csproj` automatically generates C# code during build. The generated code is included in the NuGet package for consumption by .NET services.

**Build the package:**
```bash
dotnet build
dotnet pack
```

### Python

Use the Python generation script in the contracts package:

```bash
cd vector-db-contracts/python
python scripts/generate_protos.py
```

Or use the service-level generation script:

```bash
# From vector-db-service root
scripts/generate_proto.bat    # Windows
scripts/generate_proto.sh     # Linux/macOS
```

## Benefits of This Structure

- **Maintainability**: Each domain can be maintained independently
- **Clean Imports**: Services only import the messages they need
- **Domain Separation**: Aligns with microservice boundaries and API Gateway organization
- **Scalability**: Easy to add new domains without bloating existing files
- **Single Source of Truth**: Both C# and Python generate from the same proto definitions
- **Versioning**: Domain-level versioning via package names (e.g., `vectordb.core.v1`)

## Publishing

### NuGet Package (C#)
The C# contracts are automatically packaged and can be published to NuGet for consumption by other .NET services.

### PyPI Package (Python)
The Python contracts package is located in `../python/` and can be published to PyPI for consumption by Python services.

## Version Management

Version is managed in the `../../VERSION` file at the repository root.

