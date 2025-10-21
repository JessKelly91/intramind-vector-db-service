"""
gRPC Server for Vector Database Service.

Starts the gRPC server and registers the VectorDB servicer.
"""

import grpc
from concurrent import futures
import signal
import sys
import time
from datetime import datetime

from .servicers.vector_db_servicer import VectorDBServicer
from .protos import vector_service_pb2_grpc
from ..weaviate_client.config import get_settings


def serve():
    """Start the gRPC server."""
    settings = get_settings()
    
    # Get port from environment or use default
    # Note: 50051 is used by Weaviate's gRPC, so we use 50052
    port = settings.get('GrpcServer.Port', '50052')
    max_workers = int(settings.get('GrpcServer.MaxWorkers', '10'))
    
    # Create server with thread pool
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=max_workers),
        options=[
            ('grpc.max_send_message_length', 100 * 1024 * 1024),  # 100MB
            ('grpc.max_receive_message_length', 100 * 1024 * 1024),  # 100MB
        ]
    )
    
    # Register servicer
    try:
        servicer = VectorDBServicer()
        vector_service_pb2_grpc.add_VectorDBServiceServicer_to_server(servicer, server)
        print(f"✅ VectorDBServicer registered successfully")
    except Exception as e:
        print(f"❌ Failed to register servicer: {e}")
        sys.exit(1)
    
    # Bind to port
    server_address = f'[::]:{port}'
    server.add_insecure_port(server_address)
    
    # Start server
    server.start()
    
    start_time = datetime.now()
    print("=" * 60)
    print("🚀 Vector Database gRPC Server")
    print("=" * 60)
    print(f"Environment: {settings.environment_value}")
    print(f"Server Address: {server_address}")
    print(f"Max Workers: {max_workers}")
    print(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print("Server is running. Press Ctrl+C to stop.")
    print()
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print("\n\n🛑 Shutting down gracefully...")
        server.stop(grace=5)
        uptime = datetime.now() - start_time
        print(f"Server was running for: {uptime}")
        print("✅ Server stopped")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Keep server running
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == '__main__':
    serve()

