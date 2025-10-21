# vectordb-contracts

Python gRPC client and server code for the Vector Database Service.

[![PyPI version](https://img.shields.io/pypi/v/vectordb-contracts)](https://pypi.org/project/vectordb-contracts/)
[![Python versions](https://img.shields.io/pypi/pyversions/vectordb-contracts)](https://pypi.org/project/vectordb-contracts/)
[![License](https://img.shields.io/pypi/l/vectordb-contracts)](https://github.com/JessKelly91/ai-vector-db-practice/blob/main/LICENSE)

This package provides Protocol Buffer definitions and generated Python code for interacting with the Vector Database Service via gRPC.

## Installation

```bash
pip install vectordb-contracts
```

### For Development

```bash
pip install vectordb-contracts[dev]
```

## Requirements

- Python 3.9 or later
- grpcio >= 1.60.0
- protobuf >= 4.25.0

## Quick Start

### Client Example

```python
import grpc
from vectordb_contracts import vector_service_pb2
from vectordb_contracts import vector_service_pb2_grpc

# Create a gRPC channel
channel = grpc.insecure_channel('localhost:50051')

# Create a client stub
client = vector_service_pb2_grpc.VectorDBServiceStub(channel)

# Insert a vector
request = vector_service_pb2.InsertVectorRequest(
    collection_name="documents",
    content="This is a sample document for vectorization",
    correlation_id="request-123"
)

try:
    response = client.InsertVector(request)
    if response.success:
        print(f"✓ Vector inserted with ID: {response.id}")
    else:
        print(f"✗ Error: {response.error_message}")
except grpc.RpcError as e:
    print(f"gRPC error: {e.code()}: {e.details()}")
```

### Server Example

```python
from concurrent import futures
import grpc
from vectordb_contracts import vector_service_pb2
from vectordb_contracts import vector_service_pb2_grpc

class VectorDBServicer(vector_service_pb2_grpc.VectorDBServiceServicer):
    """Implementation of VectorDB service."""
    
    def InsertVector(self, request, context):
        """Handle InsertVector requests."""
        # Your implementation here
        return vector_service_pb2.VectorResponse(
            id="vector-123",
            content=request.content,
            success=True
        )
    
    def SemanticSearch(self, request, context):
        """Handle SemanticSearch requests."""
        # Your implementation here
        results = [
            vector_service_pb2.SearchResult(
                id="vec-1",
                content="Similar document 1",
                score=0.95
            )
        ]
        return vector_service_pb2.SearchResponse(
            results=results,
            total_count=1,
            success=True
        )

# Start server
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    vector_service_pb2_grpc.add_VectorDBServiceServicer_to_server(
        VectorDBServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
```

## Available Operations

### Vector Operations

- **InsertVector** - Insert a single vector into a collection
- **InsertVectorBatch** - Insert multiple vectors at once
- **GetVector** - Retrieve a vector by its ID
- **UpdateVector** - Update an existing vector
- **DeleteVector** - Delete a vector from a collection

### Search Operations

- **SemanticSearch** - Perform semantic similarity search
- **StreamSearch** - Stream search results (server-side streaming)

### Collection Operations

- **CreateCollection** - Create a new vector collection
- **ListCollections** - List all available collections
- **GetCollection** - Get details about a specific collection
- **DeleteCollection** - Delete a collection and all its vectors

### Health Check

- **HealthCheck** - Check service health and status

## Message Types

All message types are available in the `vector_service_pb2` module:

```python
from vectordb_contracts import vector_service_pb2

# Request messages
request = vector_service_pb2.InsertVectorRequest(...)
search_req = vector_service_pb2.SearchRequest(...)
collection_req = vector_service_pb2.CreateCollectionRequest(...)

# Response messages
response = vector_service_pb2.VectorResponse(...)
search_resp = vector_service_pb2.SearchResponse(...)
```

## Advanced Usage

### With Metadata and Filters

```python
# Insert with metadata
request = vector_service_pb2.InsertVectorRequest(
    collection_name="documents",
    content="Sample document",
    metadata={
        "author": "John Doe",
        "category": "technical",
        "created_at": "2024-01-01"
    },
    correlation_id="req-456"
)

# Search with filters
search_request = vector_service_pb2.SearchRequest(
    collection_name="documents",
    query="machine learning concepts",
    limit=10,
    return_metadata=True,
    filters={
        "category": "technical"
    },
    correlation_id="search-789"
)
```

### Async/Await Support

```python
import grpc
from vectordb_contracts import vector_service_pb2_grpc

# Create async channel
async with grpc.aio.insecure_channel('localhost:50051') as channel:
    client = vector_service_pb2_grpc.VectorDBServiceStub(channel)
    
    request = vector_service_pb2.InsertVectorRequest(
        collection_name="documents",
        content="Async insert example"
    )
    
    response = await client.InsertVector(request)
    print(f"Vector ID: {response.id}")
```

### Streaming Search

```python
# Server-side streaming search
search_request = vector_service_pb2.SearchRequest(
    collection_name="documents",
    query="search query",
    limit=100
)

# Iterate over streaming results
for result in client.StreamSearch(search_request):
    print(f"ID: {result.id}, Score: {result.score}")
    print(f"Content: {result.content}")
```

## Configuration

### Channel Options

```python
import grpc

# Configure channel with options
options = [
    ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50MB
    ('grpc.max_receive_message_length', 50 * 1024 * 1024),
    ('grpc.keepalive_time_ms', 30000),
]

channel = grpc.insecure_channel('localhost:50051', options=options)
```

### TLS/SSL

```python
import grpc

# For production, use secure channel
with open('server.crt', 'rb') as f:
    credentials = grpc.ssl_channel_credentials(f.read())

channel = grpc.secure_channel('vectordb.example.com:443', credentials)
client = vector_service_pb2_grpc.VectorDBServiceStub(channel)
```

## Error Handling

```python
import grpc

try:
    response = client.InsertVector(request)
    if not response.success:
        print(f"Operation failed: {response.error_message}")
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.UNAVAILABLE:
        print("Service is unavailable")
    elif e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
        print("Request timed out")
    else:
        print(f"gRPC error: {e.code()}: {e.details()}")
```

## Development

### Building from Source

```bash
# Clone the repository
git clone https://github.com/JessKelly91/ai-vector-db-practice.git
cd ai-vector-db-practice/vector-db-contracts/python

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Generate protobuf code
python scripts/generate_protos.py

# Build package
python scripts/build_package.py
```

### Running Tests

```bash
pytest tests/
```

## Links

- **GitHub Repository**: https://github.com/JessKelly91/ai-vector-db-practice
- **Issue Tracker**: https://github.com/JessKelly91/ai-vector-db-practice/issues
- **PyPI Package**: https://pypi.org/project/vectordb-contracts/
- **C# NuGet Package**: https://www.nuget.org/packages/VectorDB.Contracts/

## Related Packages

This Python package is part of a dual-publishing strategy. The C#/.NET version is available as:

```bash
dotnet add package VectorDB.Contracts
```

Both packages are generated from the same Protocol Buffer definitions, ensuring compatibility across platforms.

## License

MIT License - see the [LICENSE](https://github.com/JessKelly91/ai-vector-db-practice/blob/main/LICENSE) file for details.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/JessKelly91/ai-vector-db-practice).

