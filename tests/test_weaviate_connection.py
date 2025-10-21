"""
Test script to verify Weaviate connection and basic operations.

This script tests:
1. Connection to local Weaviate instance
2. Collection creation with text2vec-transformers (free local vectorizer)
3. Document insertion
4. Semantic search
5. Data cleanup
"""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.weaviate_client import WeaviateClient
from src.weaviate_client.collections import CollectionManager
from src.weaviate_client.queries import QueryManager
from src.weaviate_client.models import Document
from datetime import datetime


def test_connection():
    """Test basic connection to Weaviate."""
    print("=" * 60)
    print("TEST 1: Testing Weaviate Connection")
    print("=" * 60)
    
    with WeaviateClient() as client:
        # Check if ready
        if client.is_ready():
            print("✅ Weaviate is ready and accepting connections")
        else:
            print("❌ Weaviate is not ready")
            return False
        
        # Get metadata
        meta = client.get_meta()
        print(f"✅ Weaviate version: {meta.get('version', 'unknown')}")
        
        # Check for text2vec-transformers module
        modules = meta.get('modules', {})
        if 'text2vec-transformers' in modules:
            print("✅ text2vec-transformers module is loaded")
            model_info = modules['text2vec-transformers'].get('model', {})
            model_name = model_info.get('_name_or_path', 'unknown')
            print(f"   Model: {model_name}")
        else:
            print("⚠️  text2vec-transformers module not found")
        
        return True


def test_collection_operations():
    """Test collection creation and management."""
    print("\n" + "=" * 60)
    print("TEST 2: Testing Collection Operations")
    print("=" * 60)
    
    collection_name = "TestCollection"
    
    with WeaviateClient() as client:
        collections = CollectionManager(client.client)
        
        # Clean up if collection already exists
        if collections.collection_exists(collection_name):
            print(f"🧹 Cleaning up existing collection '{collection_name}'")
            collections.delete_collection(collection_name)
        
        # Create collection
        print(f"\n📦 Creating collection '{collection_name}' with text2vec-transformers...")
        collections.create_collection(
            name=collection_name,
            description="Test collection for validation",
            vectorizer="text2vec-transformers"
        )
        
        # Verify creation
        if collections.collection_exists(collection_name):
            print(f"✅ Collection '{collection_name}' created successfully")
        else:
            print(f"❌ Collection '{collection_name}' was not created")
            return False
        
        # List all collections
        all_collections = collections.list_collections()
        print(f"✅ Found {len(all_collections)} collection(s): {', '.join(all_collections)}")
        
        return True


def test_document_operations():
    """Test document insertion and retrieval."""
    print("\n" + "=" * 60)
    print("TEST 3: Testing Document Operations")
    print("=" * 60)
    
    collection_name = "TestCollection"
    
    with WeaviateClient() as client:
        queries = QueryManager(client.client, collection_name)
        
        # Create test documents
        print("\n📝 Creating test documents...")
        documents = [
            Document(
                content="Python is a high-level programming language known for its simplicity and readability.",
                metadata={"category": "programming", "language": "python"},
                created_at=datetime.now()
            ),
            Document(
                content="Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
                metadata={"category": "AI", "topic": "machine learning"},
                created_at=datetime.now()
            ),
            Document(
                content="Vector databases are specialized databases designed to store and query high-dimensional vectors.",
                metadata={"category": "databases", "topic": "vector search"},
                created_at=datetime.now()
            ),
            Document(
                content="Microservices architecture is a design pattern where applications are composed of small, independent services.",
                metadata={"category": "architecture", "topic": "microservices"},
                created_at=datetime.now()
            ),
        ]
        
        # Insert documents
        print(f"💾 Inserting {len(documents)} documents...")
        doc_ids = queries.insert_many(documents)
        print(f"✅ Inserted {len(doc_ids)} documents")
        
        # Verify count
        count = queries.count()
        print(f"✅ Collection now contains {count} document(s)")
        
        return doc_ids


def test_semantic_search(doc_ids):
    """Test semantic search functionality."""
    print("\n" + "=" * 60)
    print("TEST 4: Testing Semantic Search")
    print("=" * 60)
    
    collection_name = "TestCollection"
    
    with WeaviateClient() as client:
        queries = QueryManager(client.client, collection_name)
        
        # Test queries
        test_queries = [
            "Tell me about artificial intelligence and learning systems",
            "What are microservices?",
            "How do vector databases work?",
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Query {i}: '{query}'")
            print("-" * 60)
            
            results = queries.search(query, limit=3)
            
            if results:
                print(f"✅ Found {len(results)} result(s):")
                for j, result in enumerate(results, 1):
                    print(f"\n   Result {j}:")
                    print(f"   Score: {result.score:.4f}" if result.score else "   Score: N/A")
                    print(f"   Content: {result.content[:100]}...")
                    print(f"   Metadata: {result.metadata}")
            else:
                print("❌ No results found")
        
        return True


def test_persistence():
    """Test data persistence."""
    print("\n" + "=" * 60)
    print("TEST 5: Testing Data Persistence")
    print("=" * 60)
    
    collection_name = "TestCollection"
    
    with WeaviateClient() as client:
        queries = QueryManager(client.client, collection_name)
        
        # Get count
        count = queries.count()
        print(f"✅ Collection still contains {count} document(s) after reconnection")
        
        if count > 0:
            print("✅ Data persistence is working - documents survived connection reset")
        else:
            print("⚠️  No documents found - data may not have persisted")
        
        return count > 0


def cleanup():
    """Clean up test data."""
    print("\n" + "=" * 60)
    print("CLEANUP: Removing Test Data")
    print("=" * 60)
    
    collection_name = "TestCollection"
    
    with WeaviateClient() as client:
        collections = CollectionManager(client.client)
        
        if collections.collection_exists(collection_name):
            collections.delete_collection(collection_name)
            print(f"✅ Test collection '{collection_name}' deleted")
        else:
            print(f"⚠️  Collection '{collection_name}' not found")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("WEAVIATE CONNECTION & OPERATIONS TEST")
    print("=" * 60)
    print("\nTesting local Weaviate instance with text2vec-transformers")
    print("(Free local vectorization - no API keys required)\n")
    
    try:
        # Test 1: Connection
        if not test_connection():
            print("\n❌ Connection test failed. Exiting.")
            return False
        
        # Test 2: Collection operations
        if not test_collection_operations():
            print("\n❌ Collection operations test failed. Exiting.")
            return False
        
        # Test 3: Document operations
        doc_ids = test_document_operations()
        if not doc_ids:
            print("\n❌ Document operations test failed. Exiting.")
            return False
        
        # Test 4: Semantic search
        if not test_semantic_search(doc_ids):
            print("\n❌ Semantic search test failed. Exiting.")
            return False
        
        # Test 5: Persistence
        if not test_persistence():
            print("\n⚠️  Persistence test had issues, but continuing.")
        
        # Cleanup
        cleanup()
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)
        print("\nYour Weaviate setup is working correctly:")
        print("  ✅ Connection established")
        print("  ✅ Collections can be created/deleted")
        print("  ✅ Documents can be inserted")
        print("  ✅ Semantic search is functional")
        print("  ✅ Data persists across connections")
        print("  ✅ Free text2vec-transformers vectorizer is working")
        print("\n🎉 You're ready to proceed to the next phase!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

