# UniControl Backend Dockerfile
# =============================
# Multi-stage build for production

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r unicontrol && useradd -r -g unicontrol unicontrol

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY --chown=unicontrol:unicontrol . .

# Create logs and uploads directories
RUN mkdir -p /app/logs /app/uploads/receipts && chown -R unicontrol:unicontrol /app/logs /app/uploads

# Make entrypoint executable
COPY --chown=unicontrol:unicontrol docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Switch to non-root user
USER unicontrol

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run entrypoint script (migrations + uvicorn)
ENTRYPOINT ["/app/docker-entrypoint.sh"]
