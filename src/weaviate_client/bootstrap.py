"""
Bootstrap module for initializing application components.

This module handles initialization of:
- Configuration loading (from JSON files and environment variables)
- Application Insights telemetry
- Logging setup
"""

from typing import Optional
from .config import get_settings
from .telemetry import initialize_telemetry, get_telemetry_client


def initialize_application(
    enable_telemetry: bool = True
) -> dict:
    """
    Initialize application configuration and telemetry.

    This should be called once at application startup.

    Args:
        enable_telemetry: Whether to initialize Application Insights telemetry

    Returns:
        Dictionary with initialization results:
        {
            'settings': Settings instance,
            'telemetry': TelemetryClient instance or None,
            'environment': environment name
        }
    """
    print("=" * 60)
    print("Initializing Application")
    print("=" * 60)

    # Load configuration from JSON files and environment variables
    settings = get_settings()
    environment = settings.environment_value
    print(f"Environment: {environment}")

    # Initialize telemetry if enabled and configured
    telemetry = None
    if enable_telemetry:
        connection_string = settings.application_insights_connection_string
        if connection_string:
            try:
                telemetry = initialize_telemetry(
                    connection_string=connection_string,
                    application_id=settings.application_id,
                    log_level=settings.serilog_minimum_level,
                    enable_metrics=True
                )
                print(f"Application Insights initialized for environment: {environment}")

                # Track startup event
                telemetry.track_event(
                    "ApplicationStartup",
                    properties={
                        "environment": environment,
                        "application_id": settings.application_id
                    }
                )

            except Exception as e:
                print(f"Warning: Failed to initialize Application Insights: {e}")
        else:
            print("Application Insights connection string not configured - skipping telemetry")

    print("=" * 60)
    print("Application Initialized Successfully")
    print("=" * 60)

    return {
        'settings': settings,
        'telemetry': telemetry,
        'environment': environment
    }


def shutdown_application():
    """
    Gracefully shutdown application components.

    Call this during application shutdown to flush telemetry and cleanup resources.
    """
    print("Shutting down application...")

    telemetry = get_telemetry_client()
    if telemetry:
        try:
            # Track shutdown event
            telemetry.track_event("ApplicationShutdown")

            # Flush telemetry
            telemetry.flush()
            print("Telemetry flushed successfully")

        except Exception as e:
            print(f"Warning: Failed to flush telemetry during shutdown: {e}")

    print("Application shutdown complete")
