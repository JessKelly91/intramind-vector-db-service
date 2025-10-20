import weaviate
from weaviate.classes.init import Auth
from typing import Optional, List, Dict, Any
from .config import get_settings


class WeaviateClient:
    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize Weaviate client.

        Args:
            url: Weaviate instance URL (defaults to appSettings.json)
            api_key: API key for authentication (defaults to appSettings.json)
        """
        settings = get_settings()
        self.url = url or settings.weaviate_url or 'http://localhost:8080'
        self.api_key = api_key or settings.weaviate_api_key
        self.client = None

    def connect(self):
        """Establish connection to Weaviate instance."""
        try:
            if self.api_key:
                self.client = weaviate.connect_to_weaviate_cloud(
                    cluster_url=self.url,
                    auth_credentials=Auth.api_key(self.api_key)
                )
            else:
                self.client = weaviate.connect_to_local(host=self.url.replace('http://', '').replace('https://', ''))

            print(f"Connected to Weaviate at {self.url}")
            return self.client
        except Exception as e:
            print(f"Failed to connect to Weaviate: {e}")
            raise

    def disconnect(self):
        """Close connection to Weaviate instance."""
        if self.client:
            self.client.close()
            print("Disconnected from Weaviate")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def is_ready(self) -> bool:
        """Check if Weaviate instance is ready."""
        if not self.client:
            return False
        return self.client.is_ready()

    def get_meta(self) -> Dict[str, Any]:
        """Get metadata about the Weaviate instance."""
        if not self.client:
            raise ConnectionError("Client not connected. Call connect() first.")
        return self.client.get_meta()
