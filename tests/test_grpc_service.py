"""
Test script for gRPC Vector Database Service.

Tests all RPC methods end-to-end.
"""

import grpc
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.service.protos import vector_service_pb2, vector_service_pb2_grpc


def test_health_check(stub):
    """Test the health check endpoint."""
    print("=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    
    try:
        request = vector_service_pb2.HealthCheckRequest(service="vectordb")
        response = stub.HealthCheck(request)
        
        status_map = {
            0: "UNKNOWN",
            1: "SERVING",
            2: "NOT_SERVING",
            3: "SERVICE_UNKNOWN"
        }
        
        print(f"✅ Status: {status_map.get(response.status, 'UNKNOWN')}")
        print(f"✅ Weaviate Status: {response.weaviate_status}")
        print(f"✅ Version: {response.version}")
        print(f"✅ Environment: {response.environment}")
        
        if response.status == 1:
            print("✅ Service is healthy and ready")
            return True
        else:
            print("❌ Service is not healthy")
            return False
            
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_collection_operations(stub):
    """Test collection CRUD operations."""
    print("\n" + "=" * 60)
    print("TEST 2: Collection Operations")
    print("=" * 60)
    
    collection_name = "GrpcTestCollection"
    
    try:
        # Create collection
        print(f"\n📦 Creating collection '{collection_name}'...")
        create_request = vector_service_pb2.CreateCollectionRequest(
            collection_name=collection_name,
            description="gRPC test collection",
            vectorizer="text2vec-transformers",
            correlation_id="test-create-001"
        )
        create_response = stub.CreateCollection(create_request)
        
        if create_response.success:
            print(f"✅ Collection '{collection_name}' created successfully")
        else:
            print(f"❌ Failed to create collection: {create_response.error_message}")
            return False
        
        # List collections
        print(f"\n📋 Listing all collections...")
        list_request = vector_service_pb2.ListCollectionsRequest(
            correlation_id="test-list-001"
        )
        list_response = stub.ListCollections(list_request)
        
        if list_response.success:
            print(f"✅ Found {list_response.total_count} collection(s):")
            for name in list_response.collection_names:
                print(f"   - {name}")
        else:
            print(f"❌ Failed to list collections: {list_response.error_message}")
            return False
        
        # Get collection info
        print(f"\n🔍 Getting collection info...")
        get_request = vector_service_pb2.GetCollectionRequest(
            collection_name=collection_name,
            correlation_id="test-get-001"
        )
        get_response = stub.GetCollection(get_request)
        
        if get_response.success:
            print(f"✅ Collection: {get_response.name}")
            print(f"✅ Document count: {get_response.document_count}")
        else:
            print(f"❌ Failed to get collection: {get_response.error_message}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Collection operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_document_operations(stub):
    """Test document insert and retrieval."""
    print("\n" + "=" * 60)
    print("TEST 3: Document Operations")
    print("=" * 60)
    
    collection_name = "GrpcTestCollection"
    
    try:
        # Insert single document
        print(f"\n📝 Inserting single document...")
        insert_request = vector_service_pb2.InsertVectorRequest(
            collection_name=collection_name,
            content="Python is a high-level programming language.",
            metadata={"category": "programming", "language": "python"},
            correlation_id="test-insert-001",
            created_at=datetime.now().isoformat()
        )
        insert_response = stub.InsertVector(insert_request)
        
        if insert_response.success:
            doc_id = insert_response.id
            print(f"✅ Document inserted with ID: {doc_id}")
        else:
            print(f"❌ Failed to insert document: {insert_response.error_message}")
            return False, None
        
        # Insert batch
        print(f"\n💾 Inserting batch of documents...")
        documents = [
            vector_service_pb2.VectorDocument(
                content="Machine learning is a subset of artificial intelligence.",
                metadata={"category": "AI", "topic": "machine learning"},
                created_at=datetime.now().isoformat()
            ),
            vector_service_pb2.VectorDocument(
                content="Vector databases store high-dimensional vectors.",
                metadata={"category": "databases", "topic": "vector search"},
                created_at=datetime.now().isoformat()
            ),
            vector_service_pb2.VectorDocument(
                content="Microservices architecture uses small independent services.",
                metadata={"category": "architecture", "topic": "microservices"},
                created_at=datetime.now().isoformat()
            ),
        ]
        
        batch_request = vector_service_pb2.InsertVectorBatchRequest(
            collection_name=collection_name,
            documents=documents,
            correlation_id="test-batch-001"
        )
        batch_response = stub.InsertVectorBatch(batch_request)
        
        if batch_response.success:
            print(f"✅ Inserted {batch_response.total_inserted} documents")
            print(f"✅ Failed: {batch_response.total_failed}")
        else:
            print(f"❌ Batch insert failed: {batch_response.error_message}")
            return False, None
        
        # Get document by ID
        print(f"\n🔍 Retrieving document by ID...")
        get_request = vector_service_pb2.GetVectorRequest(
            collection_name=collection_name,
            vector_id=doc_id,
            correlation_id="test-get-001"
        )
        get_response = stub.GetVector(get_request)
        
        if get_response.success:
            print(f"✅ Retrieved document:")
            print(f"   ID: {get_response.id}")
            print(f"   Content: {get_response.content[:50]}...")
            print(f"   Metadata: {dict(get_response.metadata)}")
        else:
            print(f"❌ Failed to get document: {get_response.error_message}")
            return False, None
        
        return True, doc_id
        
    except Exception as e:
        print(f"❌ Document operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_semantic_search(stub):
    """Test semantic search."""
    print("\n" + "=" * 60)
    print("TEST 4: Semantic Search")
    print("=" * 60)
    
    collection_name = "GrpcTestCollection"
    
    try:
        queries = [
            "Tell me about artificial intelligence",
            "What are microservices?",
            "Explain vector databases"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\n🔍 Query {i}: '{query}'")
            print("-" * 60)
            
            search_request = vector_service_pb2.SearchRequest(
                collection_name=collection_name,
                query=query,
                limit=3,
                correlation_id=f"test-search-{i:03d}",
                return_metadata=True
            )
            
            search_response = stub.SemanticSearch(search_request)
            
            if search_response.success:
                print(f"✅ Found {search_response.total_count} result(s)")
                print(f"✅ Duration: {search_response.duration_ms:.2f}ms")
                
                for j, result in enumerate(search_response.results, 1):
                    print(f"\n   Result {j}:")
                    print(f"   Score: {result.score:.4f}" if result.score else "   Score: N/A")
                    print(f"   Content: {result.content[:80]}...")
                    print(f"   Metadata: {dict(result.metadata)}")
            else:
                print(f"❌ Search failed: {search_response.error_message}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Semantic search failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_delete_operations(stub, doc_id):
    """Test delete operations."""
    print("\n" + "=" * 60)
    print("TEST 5: Delete Operations")
    print("=" * 60)
    
    collection_name = "GrpcTestCollection"
    
    try:
        # Delete document
        if doc_id:
            print(f"\n🗑️  Deleting document {doc_id}...")
            delete_doc_request = vector_service_pb2.DeleteVectorRequest(
                collection_name=collection_name,
                vector_id=doc_id,
                correlation_id="test-delete-doc-001"
            )
            delete_doc_response = stub.DeleteVector(delete_doc_request)
            
            if delete_doc_response.success:
                print(f"✅ {delete_doc_response.message}")
            else:
                print(f"⚠️  Delete document: {delete_doc_response.error_message}")
        
        # Delete collection
        print(f"\n🗑️  Deleting collection '{collection_name}'...")
        delete_coll_request = vector_service_pb2.DeleteCollectionRequest(
            collection_name=collection_name,
            correlation_id="test-delete-coll-001"
        )
        delete_coll_response = stub.DeleteCollection(delete_coll_request)
        
        if delete_coll_response.success:
            print(f"✅ {delete_coll_response.message}")
        else:
            print(f"❌ Delete collection failed: {delete_coll_response.error_message}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Delete operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("gRPC VECTOR DATABASE SERVICE TEST")
    print("=" * 60)
    print("\nConnecting to gRPC server at localhost:50052...")
    
    # Create channel and stub
    channel = grpc.insecure_channel('localhost:50052')
    stub = vector_service_pb2_grpc.VectorDBServiceStub(channel)
    
    try:
        # Run tests
        results = []
        
        # Test 1: Health Check
        results.append(("Health Check", test_health_check(stub)))
        
        # Test 2: Collection Operations
        results.append(("Collection Operations", test_collection_operations(stub)))
        
        # Test 3: Document Operations
        doc_success, doc_id = test_document_operations(stub)
        results.append(("Document Operations", doc_success))
        
        # Test 4: Semantic Search
        results.append(("Semantic Search", test_semantic_search(stub)))
        
        # Test 5: Delete Operations
        results.append(("Delete Operations", test_delete_operations(stub, doc_id)))
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name:.<40} {status}")
        
        print("=" * 60)
        print(f"Total: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! gRPC service is working correctly.")
            return 0
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")
            return 1
            
    except grpc.RpcError as e:
        print(f"\n❌ gRPC Error: {e.code()} - {e.details()}")
        print("\nMake sure the gRPC server is running:")
        print("  python -m src.service.server")
        return 1
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        channel.close()


if __name__ == "__main__":
    sys.exit(main())

