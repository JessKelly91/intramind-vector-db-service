"""
vectordb-contracts - Protocol Buffer contracts for Vector Database gRPC Service

This package provides Python gRPC client and server code for the Vector Database Service.
The protobuf definitions are shared with the C# NuGet package VectorDB.Contracts.

Usage:
    from vectordb_contracts import vector_service_pb2
    from vectordb_contracts import vector_service_pb2_grpc
    
    # Create a gRPC channel
    channel = grpc.insecure_channel('localhost:50051')
    
    # Create a client stub
    client = vector_service_pb2_grpc.VectorDBServiceStub(channel)
    
    # Make a request
    request = vector_service_pb2.InsertVectorRequest(
        collection_name="my_collection",
        content="Sample text",
        correlation_id="123"
    )
    response = client.InsertVector(request)
"""

__version__ = "1.0.0"  # This will be updated during build

# Import generated protobuf modules when they're available
try:
    from vectordb_contracts import vector_service_pb2
    from vectordb_contracts import vector_service_pb2_grpc
    
    __all__ = [
        'vector_service_pb2',
        'vector_service_pb2_grpc',
    ]
except ImportError:
    # Generated files not available yet (e.g., during initial setup)
    __all__ = []

