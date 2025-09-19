# Production Dockerfile for NFL Simulation Motor
# Multi-stage build for optimized production image

# Build stage
FROM python:3.12-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

# Set labels for image metadata
LABEL maintainer="sportieAI <contact@sportieai.com>"
LABEL org.label-schema.build-date=$BUILD_DATE
LABEL org.label-schema.name="NFL-sim-motor"
LABEL org.label-schema.description="Production-ready NFL simulation engine"
LABEL org.label-schema.url="https://github.com/sportieAI/NFL-sim-motor"
LABEL org.label-schema.vcs-ref=$VCS_REF
LABEL org.label-schema.vcs-url="https://github.com/sportieAI/NFL-sim-motor"
LABEL org.label-schema.vendor="sportieAI"
LABEL org.label-schema.version=$VERSION
LABEL org.label-schema.schema-version="1.0"

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim as production

# Install system dependencies for runtime
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /var/log/nfl-sim-motor && \
    mkdir -p /app/data && \
    mkdir -p /app/cache

# Set ownership and permissions
RUN chown -R appuser:appuser /app /var/log/nfl-sim-motor && \
    chmod +x /app/main.py

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_ENV=production

# Expose application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "main.py"]

# Development stage (optional)
FROM production as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    flake8 \
    black \
    mypy \
    ipython \
    jupyter

# Install additional development tools
RUN apt-get update && apt-get install -y \
    vim \
    git \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Switch back to appuser
USER appuser

# Set development environment
ENV APP_ENV=development
ENV PYTHONPATH=/app

# Default command for development
CMD ["python", "-m", "pytest", "-v"]