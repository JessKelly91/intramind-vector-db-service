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
            # Determine if this is a local instance
            is_local = 'localhost' in self.url.lower() or '127.0.0.1' in self.url

            if is_local:
                # Connect to local Weaviate instance
                # Parse host and port from URL
                url_without_protocol = self.url.replace('http://', '').replace('https://', '').split('/')[0]

                if ':' in url_without_protocol:
                    host, port_str = url_without_protocol.split(':')
                    port = int(port_str)
                else:
                    host = url_without_protocol
                    port = 8080  # Default Weaviate port

                # Use connect_to_local for localhost
                self.client = weaviate.connect_to_local(host=host, port=port)
            else:
                # Check if this is a Weaviate Cloud instance
                is_weaviate_cloud = '.weaviate.network' in self.url.lower() or '.weaviate.cloud' in self.url.lower()

                if is_weaviate_cloud:
                    # Weaviate Cloud requires API key
                    if not self.api_key:
                        raise ValueError("API key required for Weaviate Cloud instances")

                    self.client = weaviate.connect_to_weaviate_cloud(
                        cluster_url=self.url,
                        auth_credentials=Auth.api_key(self.api_key)
                    )
                else:
                    # Custom/self-hosted instance (e.g., Docker Compose)
                    # Support both authenticated and anonymous access
                    from weaviate.classes.init import AdditionalConfig, Timeout

                    # Parse the URL to extract http_host, http_port, and http_secure
                    http_secure = self.url.startswith('https://')
                    url_without_protocol = self.url.replace('http://', '').replace('https://', '').split('/')[0]

                    if ':' in url_without_protocol:
                        http_host, port_str = url_without_protocol.split(':')
                        http_port = int(port_str)
                    else:
                        http_host = url_without_protocol
                        http_port = 443 if http_secure else 8080

                    # Build connection params
                    if self.api_key:
                        auth_credentials = Auth.api_key(self.api_key)
                    else:
                        auth_credentials = None

                    self.client = weaviate.connect_to_custom(
                        http_host=http_host,
                        http_port=http_port,
                        http_secure=http_secure,
                        grpc_host=http_host,
                        grpc_port=50051,
                        grpc_secure=http_secure,
                        auth_credentials=auth_credentials,
                        additional_config=AdditionalConfig(
                            timeout=Timeout(init=30, query=60, insert=120)
                        )
                    )

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
