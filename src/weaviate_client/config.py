import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


class Settings:
    """
    Configuration manager that reads from appSettings.json and environment variables.

    Production-like loading order (later sources override earlier ones):
    1. appSettings.json - Base configuration (non-secret settings only)
    2. Environment variables - Primary configuration source (from .env file or GitHub Secrets)
    
    Following 12-factor app methodology: https://12factor.net/config
    """

    def __init__(self):
        """
        Initialize settings from JSON configuration files and environment variables.
        """
        self._settings: Dict[str, Any] = {}
        self._load_dotenv()
        self._load_settings()

    def _load_dotenv(self):
        """Load environment variables from .env file if it exists."""
        project_root = Path(__file__).parent.parent.parent
        dotenv_path = project_root / '.env'
        
        if dotenv_path.exists():
            load_dotenv(dotenv_path)
            print(f"Loaded environment variables from {dotenv_path}")
        else:
            # Still call load_dotenv to pick up system environment variables
            load_dotenv()

    def _load_settings(self):
        """Load settings from JSON base configuration file."""
        project_root = Path(__file__).parent.parent.parent

        # Load base settings
        base_settings_path = project_root / 'config' / 'appSettings.json'
        if base_settings_path.exists():
            with open(base_settings_path, 'r') as f:
                self._settings = json.load(f)
        else:
            print(f"Warning: Base settings file not found at {base_settings_path}")
            self._settings = {}

        # Override settings with environment variables (primary configuration source)
        self._apply_environment_overrides()

    def _apply_environment_overrides(self):
        """Override settings with environment variables if they exist."""
        env_mappings = {
            'WEAVIATE_URL': 'Weaviate.Url',
            'WEAVIATE_KEY': 'Weaviate.ApiKey',
            'OPENAI_API_KEY': 'OpenAI.ApiKey',
            'APPINSIGHTS_CONNECTION_STRING': 'ApplicationInsights.ConnectionString',
            'ENVIRONMENT': 'Environment.Value',
            'APPLICATION_ID': 'Environment.ApplicationId',
            'GRPC_SERVER_PORT': 'GrpcServer.Port',
        }

        for env_var, setting_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                self._set_nested_value(setting_path, env_value)
                print(f"Applied environment override: {env_var}")

    def _set_nested_value(self, key_path: str, value: Any):
        """Set a nested dictionary value using dot notation."""
        keys = key_path.split('.')
        current = self._settings
        
        # Navigate to the parent dictionary
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value

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
    def all_settings(self) -> Dict[str, Any]:
        """Get all settings as dictionary."""
        return self._settings.copy()


# Global settings instance
_settings_instance: Optional[Settings] = None


def get_settings(reload: bool = False) -> Settings:
    """
    Get the global settings instance.

    Args:
        reload: Force reload settings from files and environment variables

    Returns:
        Settings instance
    """
    global _settings_instance

    if _settings_instance is None or reload:
        _settings_instance = Settings()

    return _settings_instance
