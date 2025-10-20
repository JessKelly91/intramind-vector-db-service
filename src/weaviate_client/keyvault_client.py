from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from typing import Optional, Dict
import re


class KeyVaultClient:
    """Client for interacting with Azure KeyVault."""

    def __init__(
        self,
        vault_uri: str,
        managed_identity_client_id: Optional[str] = None,
        tenant_id: Optional[str] = None
    ):
        """
        Initialize KeyVault client.

        Args:
            vault_uri: Azure KeyVault URI
            managed_identity_client_id: Client ID for managed identity (optional)
            tenant_id: Azure tenant ID (optional)
        """
        self.vault_uri = vault_uri
        self.managed_identity_client_id = managed_identity_client_id
        self.tenant_id = tenant_id
        self.client: Optional[SecretClient] = None
        self._secret_cache: Dict[str, str] = {}

    def connect(self):
        """Establish connection to Azure KeyVault."""
        try:
            if self.managed_identity_client_id:
                credential = ManagedIdentityCredential(
                    client_id=self.managed_identity_client_id
                )
                print(f"Using ManagedIdentityCredential with client_id: {self.managed_identity_client_id}")
            else:
                credential = DefaultAzureCredential()
                print("Using DefaultAzureCredential")

            self.client = SecretClient(vault_url=self.vault_uri, credential=credential)
            print(f"Connected to KeyVault at {self.vault_uri}")

        except Exception as e:
            print(f"Failed to connect to KeyVault: {e}")
            raise

    def get_secret(self, secret_name: str, use_cache: bool = True) -> Optional[str]:
        """
        Get a secret from KeyVault.

        Args:
            secret_name: Name of the secret
            use_cache: Whether to use cached value if available

        Returns:
            Secret value or None if not found
        """
        if not self.client:
            raise ConnectionError("KeyVault client not connected. Call connect() first.")

        # Check cache first
        if use_cache and secret_name in self._secret_cache:
            return self._secret_cache[secret_name]

        try:
            secret = self.client.get_secret(secret_name)
            value = secret.value

            # Cache the secret
            self._secret_cache[secret_name] = value
            print(f"Retrieved secret: {secret_name}")

            return value
        except Exception as e:
            print(f"Failed to retrieve secret '{secret_name}': {e}")
            return None

    def get_secrets_batch(self, secret_names: list[str]) -> Dict[str, Optional[str]]:
        """
        Get multiple secrets from KeyVault.

        Args:
            secret_names: List of secret names

        Returns:
            Dictionary mapping secret names to values
        """
        secrets = {}
        for name in secret_names:
            secrets[name] = self.get_secret(name)
        return secrets

    def resolve_placeholders(self, settings_dict: dict) -> dict:
        """
        Recursively resolve ${VARIABLE} placeholders in settings dictionary.

        Args:
            settings_dict: Dictionary with potential placeholders

        Returns:
            Dictionary with placeholders replaced by KeyVault secrets
        """
        if not self.client:
            raise ConnectionError("KeyVault client not connected. Call connect() first.")

        def resolve_value(value):
            if isinstance(value, str):
                # Pattern matches ${VARIABLE_NAME}
                pattern = r'\$\{([^}]+)\}'
                matches = re.findall(pattern, value)

                for match in matches:
                    secret_value = self.get_secret(match)
                    if secret_value:
                        value = value.replace(f'${{{match}}}', secret_value)
                    else:
                        print(f"Warning: Could not resolve placeholder ${{{match}}}")

                return value
            elif isinstance(value, dict):
                return {k: resolve_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve_value(item) for item in value]
            else:
                return value

        return resolve_value(settings_dict)

    def clear_cache(self):
        """Clear the secret cache."""
        self._secret_cache.clear()
        print("Secret cache cleared")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # Azure SDK handles cleanup automatically
        print("KeyVault client context closed")
