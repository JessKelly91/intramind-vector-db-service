from typing import List, Optional, Dict, Any
import json
from .models import Document, SearchResult


class QueryManager:
    """Manages queries and operations on Weaviate collections."""

    def __init__(self, client, collection_name: str):
        """
        Initialize query manager.

        Args:
            client: Connected Weaviate client instance
            collection_name: Name of the collection to query
        """
        self.client = client
        self.collection_name = collection_name
        self.collection = client.collections.get(collection_name)

    def insert(self, document: Document) -> str:
        """
        Insert a single document.

        Args:
            document: Document to insert

        Returns:
            UUID of inserted document
        """
        try:
            result = self.collection.data.insert(
                properties={
                    "content": document.content,
                    "metadata": json.dumps(document.metadata) if document.metadata else "{}",
                    "created_at": document.created_at
                }
            )
            print(f"Document inserted with ID: {result}")
            return result
        except Exception as e:
            print(f"Error inserting document: {e}")
            raise

    def insert_many(self, documents: List[Document]) -> List[str]:
        """
        Insert multiple documents in batch.

        Args:
            documents: List of documents to insert

        Returns:
            List of UUIDs for inserted documents
        """
        try:
            with self.collection.batch.dynamic() as batch:
                ids = []
                for doc in documents:
                    uuid = batch.add_object(
                        properties={
                            "content": doc.content,
                            "metadata": json.dumps(doc.metadata) if doc.metadata else "{}",
                            "created_at": doc.created_at
                        }
                    )
                    ids.append(uuid)
            print(f"Inserted {len(ids)} documents")
            return ids
        except Exception as e:
            print(f"Error inserting documents: {e}")
            raise

    def search(
        self,
        query: str,
        limit: int = 10,
        return_metadata: bool = True
    ) -> List[SearchResult]:
        """
        Semantic search using vector similarity.

        Args:
            query: Search query text
            limit: Maximum number of results
            return_metadata: Whether to return metadata

        Returns:
            List of search results
        """
        try:
            response = self.collection.query.near_text(
                query=query,
                limit=limit,
                return_metadata=['score'] if return_metadata else []
            )

            results = []
            for obj in response.objects:
                # Deserialize metadata from JSON string
                metadata_str = obj.properties.get('metadata', '{}')
                metadata = json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
                
                results.append(SearchResult(
                    id=str(obj.uuid),
                    content=obj.properties.get('content', ''),
                    score=obj.metadata.score if hasattr(obj.metadata, 'score') else None,
                    metadata=metadata
                ))

            return results
        except Exception as e:
            print(f"Error searching: {e}")
            raise

    def get_by_id(self, object_id: str) -> Optional[Document]:
        """
        Retrieve document by ID.

        Args:
            object_id: UUID of the document

        Returns:
            Document if found, None otherwise
        """
        try:
            obj = self.collection.query.fetch_object_by_id(object_id)
            if obj:
                # Deserialize metadata from JSON string
                metadata_str = obj.properties.get('metadata', '{}')
                metadata = json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
                
                return Document(
                    id=str(obj.uuid),
                    content=obj.properties.get('content', ''),
                    metadata=metadata,
                    created_at=obj.properties.get('created_at')
                )
            return None
        except Exception as e:
            print(f"Error fetching document: {e}")
            raise

    def delete(self, object_id: str):
        """Delete a document by ID."""
        try:
            self.collection.data.delete_by_id(object_id)
            print(f"Document {object_id} deleted")
        except Exception as e:
            print(f"Error deleting document: {e}")
            raise

    def count(self) -> int:
        """Get total count of documents in collection."""
        try:
            result = self.collection.aggregate.over_all(total_count=True)
            return result.total_count
        except Exception as e:
            print(f"Error counting documents: {e}")
            raise
