from typing import List, Optional, Dict, Any
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
        vectorizer: str = "text2vec-openai"
    ):
        """
        Create a new collection in Weaviate.

        Args:
            name: Collection name
            description: Collection description
            vectorizer: Vectorizer to use (default: text2vec-openai)
        """
        try:
            self.client.collections.create(
                name=name,
                description=description,
                vectorizer_config=Configure.Vectorizer.text2vec_openai(),
                properties=[
                    Property(name="content", data_type=DataType.TEXT),
                    Property(name="metadata", data_type=DataType.OBJECT),
                    Property(name="created_at", data_type=DataType.DATE),
                ]
            )
            print(f"Collection '{name}' created successfully")
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
