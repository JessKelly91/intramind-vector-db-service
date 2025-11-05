"""
gRPC Servicer for Vector Database operations.

Implements all RPC methods defined in vector_service.proto
"""

import grpc
from datetime import datetime
from typing import Iterator
from google.protobuf.timestamp_pb2 import Timestamp

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


class VectorDBServicer(vector_service_pb2_grpc.VectorServiceServicer if vector_service_pb2_grpc else object):
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
                metadata=dict(request.metadata) if request.metadata else {}
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

            # Create protobuf timestamps
            now = datetime.now()
            created_timestamp = Timestamp()
            created_timestamp.FromDatetime(now)
            updated_timestamp = Timestamp()
            updated_timestamp.FromDatetime(now)

            # Import the correct message type from Core
            from ..protos.Core import documents_messages_pb2
            
            return documents_messages_pb2.InsertVectorResponse(
                vector_id=str(doc_id),
                collection_name=request.collection_name,
                content=request.content,
                metadata=request.metadata,
                created_at=created_timestamp,
                updated_at=updated_timestamp,
                success=True
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "InsertVector"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            from ..protos.Core import documents_messages_pb2
            return documents_messages_pb2.InsertVectorResponse(
                success=False,
                error_message=str(e)
            )

    def InsertVectorBatch(self, request, context):
        """Insert multiple vectors/documents in batch."""
        try:
            # Validate we have vectors
            if not request.vectors:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("No vectors provided in batch request")
                from ..protos.Core import documents_messages_pb2
                return documents_messages_pb2.InsertVectorBatchResponse(
                    total_inserted=0,
                    total_failed=0,
                    success=False,
                    error_message="No vectors provided in batch request"
                )
            
            # Get collection name from first vector (all should be same collection)
            collection_name = request.vectors[0].collection_name
            
            # Create query manager for the collection
            query_manager = QueryManager(
                self.weaviate_client.client,
                collection_name
            )

            # Convert gRPC vectors to Document objects
            documents = [
                Document(
                    content=vec.content,
                    metadata=dict(vec.metadata) if vec.metadata else {},
                    created_at=datetime.now()
                )
                for vec in request.vectors
            ]

            # Insert all documents and get IDs
            ids = query_manager.insert_many(documents)

            # Track telemetry
            if self.telemetry:
                self.telemetry.track_metric("BatchInsertCount", len(ids))
                self.telemetry.track_event(
                    "VectorBatchInserted",
                    properties={
                        "collection": collection_name,
                        "count": str(len(ids)),
                        "correlation_id": request.correlation_id
                    }
                )

            # Create response with all inserted vectors
            from ..protos.Core import documents_messages_pb2
            now = datetime.now()
            created_timestamp = Timestamp()
            created_timestamp.FromDatetime(now)
            updated_timestamp = Timestamp()
            updated_timestamp.FromDatetime(now)
            
            response_vectors = []
            for i, (vec, doc_id) in enumerate(zip(request.vectors, ids)):
                response_vectors.append(
                    documents_messages_pb2.InsertVectorResponse(
                        vector_id=str(doc_id),
                        collection_name=vec.collection_name,
                        content=vec.content,
                        metadata=vec.metadata,
                        created_at=created_timestamp,
                        updated_at=updated_timestamp,
                        success=True
                    )
                )
            
            return documents_messages_pb2.InsertVectorBatchResponse(
                vectors=response_vectors,
                total_inserted=len(ids),
                total_failed=0,
                success=True
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "InsertVectorBatch"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            from ..protos.Core import documents_messages_pb2
            return documents_messages_pb2.InsertVectorBatchResponse(
                total_inserted=0,
                total_failed=len(request.vectors) if request.vectors else 0,
                success=False,
                error_message=str(e)
            )

    def GetVector(self, request, context):
        """Get a vector/document by ID."""
        try:
            # Import the correct message type from Core
            from ..protos.Core import documents_messages_pb2
            
            query_manager = QueryManager(
                self.weaviate_client.client,
                request.collection_name
            )

            doc = query_manager.get_by_id(request.vector_id)

            if not doc:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Vector {request.vector_id} not found")
                return documents_messages_pb2.GetVectorResponse(
                    success=False,
                    error_message="Vector not found"
                )

            # Create timestamps
            created_timestamp = Timestamp()
            if doc.created_at:
                if isinstance(doc.created_at, str):
                    created_timestamp.FromJsonString(doc.created_at)
                else:
                    created_timestamp.FromDatetime(doc.created_at)
            
            updated_timestamp = Timestamp()
            updated_timestamp.FromDatetime(datetime.now())

            return documents_messages_pb2.GetVectorResponse(
                vector_id=doc.id,
                collection_name=request.collection_name,
                content=doc.content,
                metadata=doc.metadata or {},
                created_at=created_timestamp,
                updated_at=updated_timestamp,
                success=True
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "GetVector"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            from ..protos.Core import documents_messages_pb2
            return documents_messages_pb2.GetVectorResponse(
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

            # Import the correct message type from Core
            from ..protos.Core import documents_messages_pb2
            
            return documents_messages_pb2.DeleteVectorResponse(
                success=True,
                message=f"Vector {request.vector_id} deleted successfully"
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "DeleteVector"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            # Import the correct message type from Core
            from ..protos.Core import documents_messages_pb2
            
            return documents_messages_pb2.DeleteVectorResponse(
                success=False,
                error_message=str(e)
            )

    def UpdateVector(self, request, context):
        """Update a vector/document."""
        try:
            # Import the correct message type from Core
            from ..protos.Core import documents_messages_pb2
            
            query_manager = QueryManager(
                self.weaviate_client.client,
                request.collection_name
            )

            # Prepare content and metadata (only include if provided)
            content = request.content if request.content else None
            metadata = dict(request.metadata) if request.metadata else None

            # Perform partial update
            query_manager.update(
                object_id=request.vector_id,
                content=content,
                metadata=metadata
            )

            # Retrieve the updated document to return in response
            updated_doc = query_manager.get_by_id(request.vector_id)

            if not updated_doc:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Document updated but could not be retrieved")
                return documents_messages_pb2.UpdateVectorResponse(
                    success=False,
                    error_message="Document updated but could not be retrieved"
                )

            if self.telemetry:
                self.telemetry.track_event(
                    "VectorUpdated",
                    properties={
                        "collection": request.collection_name,
                        "vector_id": request.vector_id,
                        "correlation_id": request.correlation_id
                    }
                )

            # Create timestamps
            created_timestamp = Timestamp()
            if updated_doc.created_at:
                if isinstance(updated_doc.created_at, str):
                    created_timestamp.FromJsonString(updated_doc.created_at)
                else:
                    created_timestamp.FromDatetime(updated_doc.created_at)
            
            updated_timestamp = Timestamp()
            updated_timestamp.FromDatetime(datetime.now())

            return documents_messages_pb2.UpdateVectorResponse(
                vector_id=updated_doc.id,
                collection_name=request.collection_name,
                content=updated_doc.content,
                metadata=updated_doc.metadata or {},
                created_at=created_timestamp,
                updated_at=updated_timestamp,
                success=True
            )

        except ValueError as e:
            # Document not found
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "UpdateVector"})

            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))

            from ..protos.Core import documents_messages_pb2
            return documents_messages_pb2.UpdateVectorResponse(
                success=False,
                error_message=str(e)
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "UpdateVector"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            from ..protos.Core import documents_messages_pb2
            return documents_messages_pb2.UpdateVectorResponse(
                success=False,
                error_message=str(e)
            )

    def SemanticSearch(self, request, context):
        """Perform semantic search."""
        try:
            import time
            start_time = time.time()

            # Import search messages from Core
            from ..protos.Core import search_messages_pb2

            query_manager = QueryManager(
                self.weaviate_client.client,
                request.collection_name
            )

            results = query_manager.search(
                request.query,
                limit=request.limit if request.limit > 0 else 10,
                return_metadata=request.return_metadata,
                min_score=request.min_score if hasattr(request, 'min_score') else 0.0
            )

            duration_ms = (time.time() - start_time) * 1000

            search_results = [
                search_messages_pb2.SearchResult(
                    vector_id=r.id,
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

            return search_messages_pb2.SemanticSearchResponse(
                results=search_results,
                total_count=len(results),
                execution_time_ms=int(duration_ms),
                success=True
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "SemanticSearch"})

            # Import search messages for error response
            from ..protos.Core import search_messages_pb2

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            return search_messages_pb2.SemanticSearchResponse(
                total_count=0,
                success=False,
                error_message=str(e)
            )

    def StreamSearch(self, request, context) -> Iterator:
        """Stream search results (for large result sets)."""
        try:
            # Import search messages from Core
            from ..protos.Core import search_messages_pb2

            query_manager = QueryManager(
                self.weaviate_client.client,
                request.collection_name
            )

            results = query_manager.search(
                request.query,
                limit=request.limit if request.limit > 0 else 100,
                return_metadata=request.return_metadata,
                min_score=request.min_score if hasattr(request, 'min_score') else 0.0
            )

            # Stream results one by one
            for r in results:
                yield search_messages_pb2.SearchResult(
                    vector_id=r.id,
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

            # Import the correct message type from Core
            from ..protos.Core import collections_messages_pb2
            
            # Create timestamp
            now = datetime.now()
            created_timestamp = Timestamp()
            created_timestamp.FromDatetime(now)
            
            return collections_messages_pb2.CreateCollectionResponse(
                collection_name=request.collection_name,
                description=request.description,
                vector_count=0,
                created_at=created_timestamp,
                success=True
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "CreateCollection"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            # Import the correct message type from Core
            from ..protos.Core import collections_messages_pb2
            
            return collections_messages_pb2.CreateCollectionResponse(
                collection_name="",
                description="",
                vector_count=0,
                success=False,
                error_message=str(e)
            )

    def ListCollections(self, request, context):
        """List all collections."""
        try:
            # Import the correct message type from Core
            from ..protos.Core import collections_messages_pb2
            
            collection_manager = CollectionManager(self.weaviate_client.client)
            collection_names = collection_manager.list_collections()
            
            # Create CollectionInfo objects for each collection
            collection_infos = []
            for name in collection_names:
                # Get collection details
                try:
                    details = collection_manager.get_collection(name)
                    
                    # Create timestamp
                    created_timestamp = Timestamp()
                    if details.get('created_at'):
                        created_timestamp.FromDatetime(details['created_at'])
                    
                    collection_info = collections_messages_pb2.CollectionInfo(
                        collection_name=name,
                        description=details.get('description', ''),
                        vector_count=details.get('vector_count', 0),
                        created_at=created_timestamp
                    )
                    collection_infos.append(collection_info)
                except:
                    # If we can't get details, just add basic info
                    collection_info = collections_messages_pb2.CollectionInfo(
                        collection_name=name,
                        description='',
                        vector_count=0
                    )
                    collection_infos.append(collection_info)

            return collections_messages_pb2.ListCollectionsResponse(
                collections=collection_infos,
                total_count=len(collection_infos),
                success=True
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "ListCollections"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            # Import the correct message type from Core
            from ..protos.Core import collections_messages_pb2
            
            return collections_messages_pb2.ListCollectionsResponse(
                collections=[],
                total_count=0,
                success=False,
                error_message=str(e)
            )

    def GetCollection(self, request, context):
        """Get collection information."""
        try:
            collection_manager = CollectionManager(self.weaviate_client.client)

            # Import the correct message type from Core
            from ..protos.Core import collections_messages_pb2
            
            if not collection_manager.collection_exists(request.collection_name):
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"Collection {request.collection_name} not found")
                return collections_messages_pb2.GetCollectionResponse(
                    collection_name="",
                    description="",
                    vector_count=0,
                    success=False,
                    error_message="Collection not found"
                )

            query_manager = QueryManager(
                self.weaviate_client.client,
                request.collection_name
            )
            count = query_manager.count()
            
            # Create timestamp
            now = datetime.now()
            created_timestamp = Timestamp()
            created_timestamp.FromDatetime(now)

            return collections_messages_pb2.GetCollectionResponse(
                collection_name=request.collection_name,
                description="",
                vector_count=count,
                created_at=created_timestamp,
                success=True
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "GetCollection"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            # Import the correct message type from Core
            from ..protos.Core import collections_messages_pb2
            
            return collections_messages_pb2.GetCollectionResponse(
                collection_name="",
                description="",
                vector_count=0,
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

            # Import the correct message type from Core
            from ..protos.Core import collections_messages_pb2
            
            return collections_messages_pb2.DeleteCollectionResponse(
                success=True,
                message=f"Collection {request.collection_name} deleted successfully"
            )

        except Exception as e:
            if self.telemetry:
                self.telemetry.track_exception(e, properties={"operation": "DeleteCollection"})

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))

            # Import the correct message type from Core
            from ..protos.Core import collections_messages_pb2
            
            return collections_messages_pb2.DeleteCollectionResponse(
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
