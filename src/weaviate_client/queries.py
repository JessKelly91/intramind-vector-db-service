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
            created_at_value = (
                document.created_at.isoformat() if document.created_at else __import__("datetime").datetime.now().isoformat()
            )
            result = self.collection.data.insert(
                properties={
                    "content": document.content,
                    "metadata": json.dumps(document.metadata) if document.metadata else "{}",
                    "created_at": created_at_value,
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
                    created_at_value = (
                        doc.created_at.isoformat() if doc.created_at else __import__("datetime").datetime.now().isoformat()
                    )
                    uuid = batch.add_object(
                        properties={
                            "content": doc.content,
                            "metadata": json.dumps(doc.metadata) if doc.metadata else "{}",
                            "created_at": created_at_value,
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
        return_metadata: bool = True,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """
        Semantic search using vector similarity.

        Args:
            query: Search query text
            limit: Maximum number of results
            return_metadata: Whether to return metadata
            min_score: Minimum similarity score (0.0 to 1.0) to filter results

        Returns:
            List of search results
        """
        try:
            from weaviate.classes.query import MetadataQuery
            
            response = self.collection.query.near_text(
                query=query,
                limit=limit,
                return_metadata=MetadataQuery(certainty=True, distance=True, score=True) if return_metadata else None
            )

            results = []
            for obj in response.objects:
                # Deserialize metadata from JSON string
                metadata_str = obj.properties.get('metadata', '{}')
                metadata = json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
                
                # Get similarity score from Weaviate metadata
                # Priority: certainty (most reliable) > distance > score
                score = None
                
                # Try certainty first (most reliable for text2vec-transformers)
                if hasattr(obj.metadata, 'certainty') and obj.metadata.certainty is not None and obj.metadata.certainty > 0:
                    score = obj.metadata.certainty
                # Fallback to distance (convert to certainty-like score)
                elif hasattr(obj.metadata, 'distance') and obj.metadata.distance is not None:
                    # Convert distance to certainty: certainty = 1 - (distance / 2)
                    # For cosine distance, range is 0-2, so this gives us 0-1
                    score = max(0.0, 1.0 - (obj.metadata.distance / 2.0))
                # Last resort: use score field (often returns 0.0 with some vectorizers)
                elif hasattr(obj.metadata, 'score') and obj.metadata.score is not None and obj.metadata.score > 0:
                    score = obj.metadata.score
                
                # Apply min_score filter
                if score is not None and score < min_score:
                    continue  # Skip results below min_score
                
                results.append(SearchResult(
                    id=str(obj.uuid),
                    content=obj.properties.get('content', ''),
                    score=score,
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

    def update(
        self,
        object_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an existing document (partial update).
        
        Only updates the fields that are provided. If a field is None, it won't be updated.
        
        Args:
            object_id: UUID of the document to update
            content: New content (optional)
            metadata: New metadata (optional)
        
        Returns:
            True if successful
            
        Raises:
            ValueError: If document doesn't exist
            Exception: For other errors
        """
        try:
            # First verify the document exists
            existing = self.collection.query.fetch_object_by_id(object_id)
            if not existing:
                raise ValueError(f"Document with ID {object_id} not found")
            
            # Build the properties to update
            properties_to_update = {}
            
            if content is not None:
                properties_to_update['content'] = content
            
            if metadata is not None:
                properties_to_update['metadata'] = json.dumps(metadata)
            
            # Only proceed if there's something to update
            if not properties_to_update:
                print(f"No fields to update for document {object_id}")
                return True
            
            # Perform the update
            self.collection.data.update(
                uuid=object_id,
                properties=properties_to_update
            )
            
            print(f"Document {object_id} updated successfully")
            return True
            
        except ValueError as e:
            # Re-raise ValueError for not found
            raise
        except Exception as e:
            print(f"Error updating document: {e}")
            raise

    def count(self) -> int:
        """Get total count of documents in collection."""
        try:
            result = self.collection.aggregate.over_all(total_count=True)
            return result.total_count
        except Exception as e:
            print(f"Error counting documents: {e}")
            raise
