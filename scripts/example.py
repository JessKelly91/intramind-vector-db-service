import sys
import os
from datetime import datetime
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.weaviate_client import WeaviateClient, Document
from src.weaviate_client.collections import CollectionManager
from src.weaviate_client.queries import QueryManager
from src.weaviate_client.bootstrap import initialize_application, shutdown_application
from src.weaviate_client.telemetry import get_telemetry_client


def main():
    # Initialize application (config, telemetry, logging)
    app_context = initialize_application(
        enable_keyvault=False,  # Set to True in production to resolve ${VARIABLE} placeholders
        enable_telemetry=True   # Set to False to disable Application Insights
    )

    telemetry = app_context['telemetry']

    try:
        # Track that we're starting the example
        if telemetry:
            telemetry.track_event("ExampleStarted", properties={"environment": app_context['environment']})

        with WeaviateClient() as weaviate:
            start_time = time.time()

            print(f"Weaviate is ready: {weaviate.is_ready()}")
            print(f"Weaviate meta: {weaviate.get_meta()}")

            # Track Weaviate connection as dependency
            if telemetry:
                telemetry.track_dependency(
                    "WeaviateConnection",
                    "Database",
                    (time.time() - start_time) * 1000,
                    True
                )

            collection_manager = CollectionManager(weaviate.client)

            collection_name = "Article"

            if collection_manager.collection_exists(collection_name):
                print(f"Collection '{collection_name}' already exists, deleting...")
                collection_manager.delete_collection(collection_name)

            collection_manager.create_collection(
                name=collection_name,
                description="A collection of articles"
            )

            if telemetry:
                telemetry.track_event("CollectionCreated", properties={"collection_name": collection_name})

            print(f"Available collections: {collection_manager.list_collections()}")

            query_manager = QueryManager(weaviate.client, collection_name)

            sample_documents = [
                Document(
                    content="Python is a high-level programming language known for its simplicity.",
                    metadata={"category": "programming", "language": "python"},
                    created_at=datetime.now()
                ),
                Document(
                    content="Machine learning is a subset of artificial intelligence.",
                    metadata={"category": "ai", "topic": "machine learning"},
                    created_at=datetime.now()
                ),
                Document(
                    content="Vector databases are optimized for similarity search.",
                    metadata={"category": "databases", "type": "vector"},
                    created_at=datetime.now()
                ),
            ]

            print("\nInserting documents...")
            insert_start = time.time()
            ids = query_manager.insert_many(sample_documents)
            insert_duration = (time.time() - insert_start) * 1000

            print(f"Inserted document IDs: {ids}")

            if telemetry:
                telemetry.track_metric("DocumentsInserted", len(ids))
                telemetry.track_dependency(
                    "WeaviateBatchInsert",
                    "Database",
                    insert_duration,
                    True,
                    properties={"document_count": str(len(ids))}
                )

            print(f"\nTotal documents in collection: {query_manager.count()}")

            print("\nSearching for 'artificial intelligence'...")
            search_start = time.time()
            results = query_manager.search("artificial intelligence", limit=3)
            search_duration = (time.time() - search_start) * 1000

            if telemetry:
                telemetry.track_dependency(
                    "WeaviateSearch",
                    "Database",
                    search_duration,
                    True,
                    properties={"query": "artificial intelligence", "result_count": str(len(results))}
                )

            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"  ID: {result.id}")
                print(f"  Content: {result.content}")
                print(f"  Score: {result.score}")
                print(f"  Metadata: {result.metadata}")

            if results:
                print(f"\nFetching document by ID: {results[0].id}")
                doc = query_manager.get_by_id(results[0].id)
                if doc:
                    print(f"  Content: {doc.content}")

        if telemetry:
            telemetry.track_event("ExampleCompleted", properties={"status": "success"})

    except Exception as e:
        print(f"Error occurred: {e}")
        if telemetry:
            telemetry.track_exception(e, properties={"operation": "main"})
        raise

    finally:
        # Gracefully shutdown and flush telemetry
        shutdown_application()


if __name__ == "__main__":
    main()
