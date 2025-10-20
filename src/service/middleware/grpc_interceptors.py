"""
gRPC Interceptors (middleware) for the Vector DB Service.

Provides:
- Correlation ID tracking
- Telemetry/logging
- Service-to-service authentication
"""

import grpc
import uuid
import time
from typing import Callable, Any
from ...weaviate_client.telemetry import get_telemetry_client
from ...weaviate_client.config import get_settings
import secrets


class CorrelationIdInterceptor(grpc.ServerInterceptor):
    """
    Add or extract correlation ID for request tracing.

    Correlation IDs allow you to track a request across multiple services.
    """

    def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails
    ) -> grpc.RpcMethodHandler:
        """
        Intercept gRPC call to add correlation ID.

        Args:
            continuation: Next handler in the chain
            handler_call_details: Call details including metadata

        Returns:
            RPC method handler
        """
        metadata = dict(handler_call_details.invocation_metadata)

        # Extract or generate correlation ID
        correlation_id = metadata.get('correlation-id') or metadata.get('x-correlation-id')

        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Store in context (you can access this later in servicers)
        # For now, just log it
        print(f"[{correlation_id}] {handler_call_details.method}")

        return continuation(handler_call_details)


class TelemetryInterceptor(grpc.ServerInterceptor):
    """
    Track all gRPC calls in Application Insights.

    Logs method calls, duration, and success/failure.
    """

    def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails
    ) -> grpc.RpcMethodHandler:
        """
        Intercept gRPC call for telemetry tracking.

        Args:
            continuation: Next handler in the chain
            handler_call_details: Call details

        Returns:
            RPC method handler
        """
        telemetry = get_telemetry_client()
        method = handler_call_details.method
        start_time = time.time()

        def wrapper(behavior: Callable, request_streaming: bool, response_streaming: bool):
            def wrapped_method(request, context):
                try:
                    # Call the actual method
                    response = behavior(request, context)

                    # Track successful call
                    duration_ms = (time.time() - start_time) * 1000

                    if telemetry:
                        telemetry.track_dependency(
                            dependency_name=method,
                            dependency_type="gRPC",
                            duration_ms=duration_ms,
                            success=True,
                            properties={"method": method}
                        )

                    return response

                except Exception as e:
                    # Track failed call
                    duration_ms = (time.time() - start_time) * 1000

                    if telemetry:
                        telemetry.track_dependency(
                            dependency_name=method,
                            dependency_type="gRPC",
                            duration_ms=duration_ms,
                            success=False,
                            properties={"method": method, "error": str(e)}
                        )
                        telemetry.track_exception(e, properties={"method": method})

                    raise

            return wrapped_method

        handler = continuation(handler_call_details)

        if handler and (handler.unary_unary or handler.unary_stream):
            return grpc.unary_unary_rpc_method_handler(
                wrapper(
                    handler.unary_unary if handler.unary_unary else handler.unary_stream,
                    False,
                    handler.unary_stream is not None
                ),
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer
            )

        return handler


class AuthInterceptor(grpc.ServerInterceptor):
    """
    Validate service-to-service authentication.

    Checks for X-Service-Auth header or uses Azure Managed Identity.
    """

    def intercept_service(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails
    ) -> grpc.RpcMethodHandler:
        """
        Intercept gRPC call for authentication.

        Args:
            continuation: Next handler in the chain
            handler_call_details: Call details

        Returns:
            RPC method handler
        """
        # Skip auth for health checks
        if handler_call_details.method == '/vectordb.VectorDBService/HealthCheck':
            return continuation(handler_call_details)

        metadata = dict(handler_call_details.invocation_metadata)
        settings = get_settings()

        service_auth_key = settings.get('Service.ServiceAuthKey')

        # If no auth key configured (local dev), allow all requests
        if not service_auth_key:
            return continuation(handler_call_details)

        # Check for service auth key
        auth_key = metadata.get('x-service-auth')

        if not auth_key:
            def abort(request, context):
                context.abort(
                    grpc.StatusCode.UNAUTHENTICATED,
                    'Missing x-service-auth header'
                )
            return grpc.unary_unary_rpc_method_handler(abort)

        # Constant-time comparison to prevent timing attacks
        if not secrets.compare_digest(auth_key, service_auth_key):
            def abort(request, context):
                context.abort(
                    grpc.StatusCode.UNAUTHENTICATED,
                    'Invalid service authentication key'
                )
            return grpc.unary_unary_rpc_method_handler(abort)

        # Authentication successful
        return continuation(handler_call_details)
