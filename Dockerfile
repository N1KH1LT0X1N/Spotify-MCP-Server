# Multi-stage Dockerfile for Spotify MCP Server
# Optimized for small image size and security

# Build stage
FROM python:3.12-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir build && \
    pip install --no-cache-dir -e .[all]

# Production stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY README.md LICENSE ./
COPY entrypoint.sh ./

# Create non-root user for security
RUN useradd -m -u 1000 spotify && \
    chmod +x /app/entrypoint.sh && \
    chown -R spotify:spotify /app

USER spotify

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CACHE_BACKEND=memory \
    LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Expose port (optional, for future REST API)
EXPOSE 8000

# Run the server with metrics (via entrypoint script)
CMD ["./entrypoint.sh"]
