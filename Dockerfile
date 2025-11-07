# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the proto definitions from vector-db-contracts submodule
COPY vector-db-contracts/src/VectorDB.Contracts/Protos/ ./vector-db-contracts/src/VectorDB.Contracts/Protos/

# Copy the proto generation script
COPY scripts/generate_proto.sh ./scripts/

# Copy the application code (before proto generation to create directories)
COPY src/ ./src/
COPY config/ ./config/

# Generate Protocol Buffer files
RUN chmod +x ./scripts/generate_proto.sh && \
    bash ./scripts/generate_proto.sh

# Expose gRPC port
EXPOSE 50052

# Set the Python path
ENV PYTHONPATH=/app

# Run the gRPC server
CMD ["python", "-m", "src.service.server"]

