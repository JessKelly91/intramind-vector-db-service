from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure import metrics_exporter
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module
import logging
from typing import Optional, Dict, Any
from datetime import datetime


class TelemetryClient:
    """Client for Azure Application Insights telemetry."""

    def __init__(self, connection_string: str, application_id: Optional[str] = None):
        """
        Initialize telemetry client.

        Args:
            connection_string: Application Insights connection string
            application_id: Application identifier for custom dimensions
        """
        self.connection_string = connection_string
        self.application_id = application_id
        self.logger: Optional[logging.Logger] = None
        self._metrics_exporter: Optional[metrics_exporter.MetricsExporter] = None
        self._stats = stats_module.stats
        self._view_manager = self._stats.view_manager
        self._stats_recorder = self._stats.stats_recorder

    def setup_logging(self, logger_name: str = 'weaviate_client', log_level: str = 'INFO'):
        """
        Setup logging with Application Insights.

        Args:
            logger_name: Name of the logger
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        try:
            self.logger = logging.getLogger(logger_name)
            self.logger.setLevel(getattr(logging, log_level.upper()))

            # Add Azure Log Handler
            azure_handler = AzureLogHandler(connection_string=self.connection_string)

            # Add custom dimensions to all logs
            if self.application_id:
                azure_handler.add_telemetry_processor(
                    lambda envelope: self._add_custom_properties(envelope)
                )

            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            azure_handler.setFormatter(formatter)

            # Add handler to logger
            self.logger.addHandler(azure_handler)

            # Also log to console
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            self.logger.info("Application Insights logging initialized")

        except Exception as e:
            print(f"Failed to setup Application Insights logging: {e}")
            # Fallback to basic logging
            logging.basicConfig(level=getattr(logging, log_level.upper()))
            self.logger = logging.getLogger(logger_name)

    def _add_custom_properties(self, envelope):
        """Add custom properties to telemetry envelope."""
        if self.application_id:
            envelope.data.base_data.properties['application_id'] = self.application_id
        envelope.data.base_data.properties['timestamp'] = datetime.utcnow().isoformat()
        return True

    def setup_metrics(self):
        """Setup custom metrics with Application Insights."""
        try:
            self._metrics_exporter = metrics_exporter.new_metrics_exporter(
                connection_string=self.connection_string
            )
            self._view_manager.register_exporter(self._metrics_exporter)

            print("Application Insights metrics initialized")

        except Exception as e:
            print(f"Failed to setup Application Insights metrics: {e}")

    def track_event(self, event_name: str, properties: Optional[Dict[str, Any]] = None):
        """
        Track a custom event.

        Args:
            event_name: Name of the event
            properties: Additional properties to log
        """
        if self.logger:
            extra = {'custom_dimensions': properties or {}}
            if self.application_id:
                extra['custom_dimensions']['application_id'] = self.application_id

            self.logger.info(f"EVENT: {event_name}", extra=extra)

    def track_exception(self, exception: Exception, properties: Optional[Dict[str, Any]] = None):
        """
        Track an exception.

        Args:
            exception: Exception to track
            properties: Additional properties to log
        """
        if self.logger:
            extra = {'custom_dimensions': properties or {}}
            if self.application_id:
                extra['custom_dimensions']['application_id'] = self.application_id

            self.logger.exception(f"Exception occurred: {str(exception)}", extra=extra)

    def track_metric(self, name: str, value: float, properties: Optional[Dict[str, str]] = None):
        """
        Track a custom metric.

        Args:
            name: Metric name
            value: Metric value
            properties: Additional properties (tags)
        """
        try:
            measure = measure_module.MeasureFloat(name, name, "units")
            view = view_module.View(
                name,
                name,
                [],
                measure,
                aggregation_module.LastValueAggregation()
            )
            self._view_manager.register_view(view)

            mmap = self._stats_recorder.new_measurement_map()
            tmap = tag_map_module.TagMap()

            if properties:
                for key, val in properties.items():
                    tmap.insert(key, val)

            mmap.measure_float_put(measure, value)
            mmap.record(tmap)

        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to track metric '{name}': {e}")

    def track_dependency(
        self,
        dependency_name: str,
        dependency_type: str,
        duration_ms: float,
        success: bool,
        properties: Optional[Dict[str, Any]] = None
    ):
        """
        Track a dependency call.

        Args:
            dependency_name: Name of the dependency
            dependency_type: Type (e.g., 'HTTP', 'Database')
            duration_ms: Duration in milliseconds
            success: Whether the call succeeded
            properties: Additional properties
        """
        if self.logger:
            extra = {
                'custom_dimensions': {
                    'dependency_name': dependency_name,
                    'dependency_type': dependency_type,
                    'duration_ms': duration_ms,
                    'success': success,
                    **(properties or {})
                }
            }
            if self.application_id:
                extra['custom_dimensions']['application_id'] = self.application_id

            log_level = logging.INFO if success else logging.WARNING
            self.logger.log(
                log_level,
                f"DEPENDENCY: {dependency_type} - {dependency_name} ({duration_ms}ms)",
                extra=extra
            )

    def flush(self):
        """Flush telemetry data to Application Insights."""
        if self._metrics_exporter:
            self._metrics_exporter.export_metrics()


# Global telemetry client instance
_telemetry_client: Optional[TelemetryClient] = None


def get_telemetry_client() -> Optional[TelemetryClient]:
    """
    Get the global telemetry client instance.

    Returns:
        TelemetryClient instance or None if not initialized
    """
    return _telemetry_client


def initialize_telemetry(
    connection_string: str,
    application_id: Optional[str] = None,
    log_level: str = 'INFO',
    enable_metrics: bool = True
) -> TelemetryClient:
    """
    Initialize the global telemetry client.

    Args:
        connection_string: Application Insights connection string
        application_id: Application identifier
        log_level: Logging level
        enable_metrics: Whether to enable custom metrics

    Returns:
        Initialized TelemetryClient instance
    """
    global _telemetry_client

    _telemetry_client = TelemetryClient(connection_string, application_id)
    _telemetry_client.setup_logging(log_level=log_level)

    if enable_metrics:
        _telemetry_client.setup_metrics()

    return _telemetry_client
