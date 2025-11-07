from typing import List, Optional, Dict, Any
import os
from weaviate.classes.config import Configure, Property, DataType
from .models import Document, SearchResult


class CollectionManager:
    """Manages Weaviate collections (classes/schemas)."""

    def __init__(self, client):
        """
        Initialize collection manager.

        Args:
            client: Connected Weaviate client instance
        """
        self.client = client

    def create_collection(
        self,
        name: str,
        description: str = "",
        vectorizer: str = None
    ):
        """
        Create a new collection in Weaviate.

        Args:
            name: Collection name
            description: Collection description
            vectorizer: Vectorizer to use (default: from WEAVIATE_VECTORIZER env var or 'text2vec-transformers')
                       Options: 'text2vec-transformers', 'text2vec-openai', 'none'
        """
        # Use environment variable for default vectorizer if not specified
        if vectorizer is None:
            vectorizer = os.getenv("WEAVIATE_VECTORIZER", "text2vec-transformers")
            print(f"[CollectionManager] Using vectorizer: {vectorizer} (from env: {os.getenv('WEAVIATE_VECTORIZER', 'NOT_SET')})")
        try:
            # Configure vectorizer based on the specified type
            if vectorizer == "text2vec-transformers":
                vectorizer_config = Configure.Vectorizer.text2vec_transformers()
            elif vectorizer == "text2vec-openai":
                vectorizer_config = Configure.Vectorizer.text2vec_openai()
            elif vectorizer == "none":
                vectorizer_config = Configure.Vectorizer.none()
            else:
                raise ValueError(f"Unsupported vectorizer: {vectorizer}")
            
            self.client.collections.create(
                name=name,
                description=description,
                vectorizer_config=vectorizer_config,
                properties=[
                    Property(name="content", data_type=DataType.TEXT),
                    Property(name="metadata", data_type=DataType.TEXT),  # Store as JSON string for flexibility
                    Property(name="created_at", data_type=DataType.DATE),
                ]
            )
            print(f"Collection '{name}' created successfully with {vectorizer} vectorizer")
        except Exception as e:
            print(f"Error creating collection: {e}")
            raise

    def delete_collection(self, name: str):
        """Delete a collection."""
        try:
            self.client.collections.delete(name)
            print(f"Collection '{name}' deleted successfully")
        except Exception as e:
            print(f"Error deleting collection: {e}")
            raise

    def list_collections(self) -> List[str]:
        """List all collections."""
        try:
            collections = self.client.collections.list_all()
            return [col.name for col in collections.values()]
        except Exception as e:
            print(f"Error listing collections: {e}")
            raise

    def collection_exists(self, name: str) -> bool:
        """Check if collection exists."""
        return name in self.list_collections()
