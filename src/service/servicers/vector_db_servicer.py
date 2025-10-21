"""
gRPC Servicer for Vector Database operations.

Implements all RPC methods defined in vector_service.proto
"""

import grpc
from datetime import datetime
from typing import Iterator

# These will be generated after running generate_proto script
try:
    from ..protos import vector_service_pb2, vector_service_pb2_grpc
except ImportError:
    print("Warning: Protocol Buffer files not found. Run scripts/generate_proto.bat or .sh")
    vector_service_pb2 = None
    vector_service_pb2_grpc = None

from ...weaviate_client import WeaviateClient, Document
from ...weaviate_client.collections import CollectionManager
from ...weaviate_client.queries import QueryManager

# Telemetry is optional (requires Azure opencensus libraries)
try:
    from ...weaviate_client.telemetry import get_telemetry_client
except ImportError:
    get_telemetry_client = None
    print("Info: Azure telemetry not available (opencensus not installed)")


class VectorDBServicer(vector_service_pb2_grpc.VectorDBServiceServicer if vector_service_pb2_grpc else object):
    """
    gRPC Servicer implementing Vector Database operations.
    """

    def __init__(self):
        """Initialize the servicer with Weaviate connection."""
        self.weaviate_client = WeaviateClient()
        self.weaviate_client.connect()
        self.telemetry = get_telemetry_client() if get_telemetry_client else None
        print("VectorDBServicer initialized")

    def InsertVector(self, request, context):
        """Insert a single vector/document."""
        try:
            query_manager = QueryManager(
                self.weaviate_client.client,
                request.collection_name
            )

            doc = Document(
                content=request.content,
                metadata=dict(request.metadata) if request.metadata else {},
                created_at=datetime.fromisoformat(request.created_at) if request.created_at else datetime.now()
            )

            doc_id = query_manager.insert(doc)

            if self.telemetry:
                self.telemetry.track_event(
                    "VectorInserted",
                    properties={
                        "collection": request.collection_name,
                        "correlation_id": request.correlation_id
                    }
                )

            return vector_service_pb2.VectorResponse(
                id=str(doc_id),  # Convert UUID to string
                content=request.content,
                metadata=request.metadata,
                created_at=datetime.now().isoformat(),
                success=True
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "InsertVector"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            return vector_service_pb2.VectorResponse(
                success=False,
                error_message=str(e)
            )

    def InsertVectorBatch(self, request, context):
        """Insert multiple vectors/documents in batch."""
        try:
            query_manager = QueryManager(
                self.weaviate_client.client,
                request.collection_name
            )

            documents = [
                Document(
                    content=doc.content,
                    metadata=dict(doc.metadata) if doc.metadata else {},
                    created_at=datetime.fromisoformat(doc.created_at) if doc.created_at else datetime.now()
                )
                for doc in request.documents
            ]

            ids = query_manager.insert_many(documents)

            if self.telemetry:
                self.telemetry.track_metric("BatchInsertCount", len(ids))
                self.telemetry.track_event(
                    "VectorBatchInserted",
                    properties={
                        "collection": request.collection_name,
                        "count": str(len(ids)),
                        "correlation_id": request.correlation_id
                    }
                )

            return vector_service_pb2.BatchResponse(
                ids=[str(id) for id in ids],  # Convert UUIDs to strings
                total_inserted=len(ids),
                total_failed=0,
                success=True
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "InsertVectorBatch"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            return vector_service_pb2.BatchResponse(
                total_inserted=0,
                total_failed=len(request.documents),
                success=False,
                error_message=str(e)
            )

    def GetVector(self, request, context):
        """Get a vector/document by ID."""
        try:
            query_manager = QueryManager(
                self.weaviate_client.client,
                request.collection_name
            )

            doc = query_manager.get_by_id(request.vector_id)

            if not doc:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Vector {request.vector_id} not found")
                return vector_service_pb2.VectorResponse(
                    success=False,
                    error_message="Vector not found"
                )

            return vector_service_pb2.VectorResponse(
                id=doc.id,
                content=doc.content,
                metadata=doc.metadata or {},
                created_at=doc.created_at.isoformat() if doc.created_at else "",
                success=True
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "GetVector"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            return vector_service_pb2.VectorResponse(
                success=False,
                error_message=str(e)
            )

    def DeleteVector(self, request, context):
        """Delete a vector/document by ID."""
        try:
            query_manager = QueryManager(
                self.weaviate_client.client,
                request.collection_name
            )

            query_manager.delete(request.vector_id)

            if self.telemetry:
                self.telemetry.track_event(
                    "VectorDeleted",
                    properties={
                        "collection": request.collection_name,
                        "vector_id": request.vector_id,
                        "correlation_id": request.correlation_id
                    }
                )

            return vector_service_pb2.DeleteResponse(
                success=True,
                message=f"Vector {request.vector_id} deleted successfully"
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "DeleteVector"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            return vector_service_pb2.DeleteResponse(
                success=False,
                error_message=str(e)
            )

    def UpdateVector(self, request, context):
        """Update a vector/document."""
        # Note: This is a simplified implementation
        # In practice, you'd need to implement proper update logic in queries.py
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('UpdateVector not yet implemented')
        return vector_service_pb2.VectorResponse(
            success=False,
            error_message="UpdateVector not yet implemented"
        )

    def SemanticSearch(self, request, context):
        """Perform semantic search."""
        try:
            import time
            start_time = time.time()

            query_manager = QueryManager(
                self.weaviate_client.client,
                request.collection_name
            )

            results = query_manager.search(
                request.query,
                limit=request.limit if request.limit > 0 else 10,
                return_metadata=request.return_metadata
            )

            duration_ms = (time.time() - start_time) * 1000

            search_results = [
                vector_service_pb2.SearchResult(
                    id=r.id,
                    content=r.content,
                    score=r.score or 0.0,
                    metadata=r.metadata or {}
                )
                for r in results
            ]

            if self.telemetry:
                self.telemetry.track_dependency(
                    "WeaviateSemanticSearch",
                    "Database",
                    duration_ms,
                    True,
                    properties={
                        "collection": request.collection_name,
                        "result_count": str(len(results)),
                        "correlation_id": request.correlation_id
                    }
                )

            return vector_service_pb2.SearchResponse(
                results=search_results,
                total_count=len(results),
                duration_ms=duration_ms,
                success=True
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "SemanticSearch"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            return vector_service_pb2.SearchResponse(
                total_count=0,
                success=False,
                error_message=str(e)
            )

    def StreamSearch(self, request, context) -> Iterator:
        """Stream search results (for large result sets)."""
        try:
            query_manager = QueryManager(
                self.weaviate_client.client,
                request.collection_name
            )

            results = query_manager.search(
                request.query,
                limit=request.limit if request.limit > 0 else 100,
                return_metadata=request.return_metadata
            )

            # Stream results one by one
            for r in results:
                yield vector_service_pb2.SearchResult(
                    id=r.id,
                    content=r.content,
                    score=r.score or 0.0,
                    metadata=r.metadata or {}
                )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "StreamSearch"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

    def CreateCollection(self, request, context):
        """Create a new collection."""
        try:
            collection_manager = CollectionManager(self.weaviate_client.client)

            collection_manager.create_collection(
                name=request.collection_name,
                description=request.description,
                vectorizer=request.vectorizer if request.vectorizer else "text2vec-transformers"
            )

            if self.telemetry:
                self.telemetry.track_event(
                    "CollectionCreated",
                    properties={
                        "collection": request.collection_name,
                        "correlation_id": request.correlation_id
                    }
                )

            return vector_service_pb2.CollectionResponse(
                name=request.collection_name,
                description=request.description,
                document_count=0,
                vectorizer=request.vectorizer,
                success=True
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "CreateCollection"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            return vector_service_pb2.CollectionResponse(
                success=False,
                error_message=str(e)
            )

    def ListCollections(self, request, context):
        """List all collections."""
        try:
            collection_manager = CollectionManager(self.weaviate_client.client)
            collections = collection_manager.list_collections()

            return vector_service_pb2.CollectionsResponse(
                collection_names=collections,
                total_count=len(collections),
                success=True
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "ListCollections"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            return vector_service_pb2.CollectionsResponse(
                total_count=0,
                success=False,
                error_message=str(e)
            )

    def GetCollection(self, request, context):
        """Get collection information."""
        try:
            collection_manager = CollectionManager(self.weaviate_client.client)

            if not collection_manager.collection_exists(request.collection_name):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Collection {request.collection_name} not found")
                return vector_service_pb2.CollectionResponse(
                    success=False,
                    error_message="Collection not found"
                )

            query_manager = QueryManager(
                self.weaviate_client.client,
                request.collection_name
            )
            count = query_manager.count()

            return vector_service_pb2.CollectionResponse(
                name=request.collection_name,
                document_count=count,
                success=True
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "GetCollection"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            return vector_service_pb2.CollectionResponse(
                success=False,
                error_message=str(e)
            )

    def DeleteCollection(self, request, context):
        """Delete a collection."""
        try:
            collection_manager = CollectionManager(self.weaviate_client.client)
            collection_manager.delete_collection(request.collection_name)

            if self.telemetry:
                self.telemetry.track_event(
                    "CollectionDeleted",
                    properties={
                        "collection": request.collection_name,
                        "correlation_id": request.correlation_id
                    }
                )

            return vector_service_pb2.DeleteResponse(
                success=True,
                message=f"Collection {request.collection_name} deleted successfully"
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "DeleteCollection"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            return vector_service_pb2.DeleteResponse(
                success=False,
                error_message=str(e)
            )

    def HealthCheck(self, request, context):
        """Health check endpoint."""
        try:
            is_ready = self.weaviate_client.is_ready()

            status = (
                vector_service_pb2.HealthCheckResponse.SERVING
                if is_ready
                else vector_service_pb2.HealthCheckResponse.NOT_SERVING
            )

            from ...weaviate_client.config import get_settings
            settings = get_settings()

            return vector_service_pb2.HealthCheckResponse(
                status=status,
                weaviate_status="connected" if is_ready else "disconnected",
                version="1.0.0",
                environment=settings.environment_value
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            return vector_service_pb2.HealthCheckResponse(
                status=vector_service_pb2.HealthCheckResponse.NOT_SERVING,
                weaviate_status="error",
                version="1.0.0"
            )
