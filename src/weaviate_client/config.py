import json
from pathlib import Path
from typing import Optional, Dict, Any


class Settings:
    """
    Configuration manager that reads from appSettings.json files.

    Loading order (later files override earlier ones):
    1. appSettings.json - Base settings (populated by Azure KeyVault/Pipeline variables)
    2. appSettings.Local.json - Local development overrides (gitignored)
    3. KeyVault secrets - Resolves ${VARIABLE} placeholders if enabled
    """

    def __init__(self, enable_keyvault: Optional[bool] = None):
        """
        Initialize settings from JSON configuration files.

        Args:
            enable_keyvault: Override KeyVault enable setting (useful for testing)
        """
        self._settings: Dict[str, Any] = {}
        self._keyvault_override = enable_keyvault
        self._load_settings()

    def _load_settings(self):
        """Load settings from JSON files."""
        project_root = Path(__file__).parent.parent.parent

        # Load base settings (for production/pipeline)
        base_settings_path = project_root / 'config' / 'appSettings.json'
        if base_settings_path.exists():
            with open(base_settings_path, 'r') as f:
                self._settings = json.load(f)
        else:
            print(f"Warning: Base settings file not found at {base_settings_path}")
            self._settings = {}

        # Load local settings (overrides for local development)
        local_settings_path = project_root / 'config' / 'appSettings.Local.json'
        if local_settings_path.exists():
            with open(local_settings_path, 'r') as f:
                local_settings = json.load(f)
                self._merge_settings(local_settings)
            print(f"Loaded local settings from {local_settings_path}")

        # Resolve KeyVault placeholders if enabled
        keyvault_enabled = self._keyvault_override if self._keyvault_override is not None else self._settings.get('KeyVault', {}).get('Enabled', False)
        if keyvault_enabled:
            self._resolve_keyvault_secrets()

    def _resolve_keyvault_secrets(self):
        """Resolve ${VARIABLE} placeholders using Azure KeyVault."""
        try:
            from .keyvault_client import KeyVaultClient

            keyvault_config = self._settings.get('KeyVault', {})
            vault_uri = keyvault_config.get('VaultUri')

            if not vault_uri:
                print("Warning: KeyVault enabled but VaultUri not configured")
                return

            print(f"Resolving KeyVault secrets from {vault_uri}")

            with KeyVaultClient(
                vault_uri=vault_uri,
                managed_identity_client_id=keyvault_config.get('ManagedIdentityClientId'),
                tenant_id=keyvault_config.get('TenantId')
            ) as kv_client:
                self._settings = kv_client.resolve_placeholders(self._settings)
                print("KeyVault secrets resolved successfully")

        except Exception as e:
            print(f"Failed to resolve KeyVault secrets: {e}")
            print("Continuing with placeholder values...")

    def _merge_settings(self, new_settings: Dict[str, Any]):
        """Recursively merge new settings into existing settings."""
        def merge_dict(base: dict, updates: dict):
            for key, value in updates.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value

        merge_dict(self._settings, new_settings)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value using dot notation.

        Args:
            key: Setting key (supports dot notation like 'Weaviate.Url')
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        keys = key.split('.')
        value = self._settings

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.

        Args:
            section: Section name

        Returns:
            Dictionary containing section settings
        """
        return self._settings.get(section, {})

    @property
    def weaviate_url(self) -> str:
        """Get Weaviate URL."""
        return self.get('Weaviate.Url', 'http://localhost:8080')

    @property
    def weaviate_api_key(self) -> Optional[str]:
        """Get Weaviate API key."""
        return self.get('Weaviate.ApiKey')

    @property
    def openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key."""
        return self.get('OpenAI.ApiKey')

    @property
    def default_vectorizer(self) -> str:
        """Get default vectorizer."""
        return self.get('Weaviate.DefaultVectorizer', 'text2vec-openai')

    @property
    def application_insights_connection_string(self) -> Optional[str]:
        """Get Application Insights connection string."""
        return self.get('ApplicationInsights.ConnectionString')

    @property
    def serilog_minimum_level(self) -> str:
        """Get Serilog minimum level."""
        return self.get('Serilog.MinimumLevel.Default', 'Information')

    @property
    def environment_value(self) -> str:
        """Get environment value."""
        return self.get('Environment.Value', 'Local')

    @property
    def application_id(self) -> Optional[str]:
        """Get application ID."""
        return self.get('Environment.ApplicationId')

    @property
    def keyvault_enabled(self) -> bool:
        """Check if KeyVault is enabled."""
        return self.get('KeyVault.Enabled', False)

    @property
    def keyvault_uri(self) -> Optional[str]:
        """Get KeyVault URI."""
        return self.get('KeyVault.VaultUri')

    @property
    def keyvault_managed_identity_client_id(self) -> Optional[str]:
        """Get KeyVault managed identity client ID."""
        return self.get('KeyVault.ManagedIdentityClientId')

    @property
    def keyvault_tenant_id(self) -> Optional[str]:
        """Get KeyVault tenant ID."""
        return self.get('KeyVault.TenantId')

    @property
    def all_settings(self) -> Dict[str, Any]:
        """Get all settings as dictionary."""
        return self._settings.copy()


# Global settings instance
_settings_instance: Optional[Settings] = None


def get_settings(reload: bool = False, enable_keyvault: Optional[bool] = None) -> Settings:
    """
    Get the global settings instance.

    Args:
        reload: Force reload settings from files
        enable_keyvault: Override KeyVault enable setting

    Returns:
        Settings instance
    """
    global _settings_instance

    if _settings_instance is None or reload:
        _settings_instance = Settings(enable_keyvault=enable_keyvault)

    return _settings_instance
