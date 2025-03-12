FROM python:3.12-slim-bullseye AS base

WORKDIR /app

# Install necessary dependencies once in the base image
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade preswald

FROM base

# Create a user for running the app securely
RUN useradd -m -u 1000 preswald

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/preswald /usr/local/bin/

# Set correct permissions
RUN chown -R preswald:preswald /usr/local/lib/python3.12/site-packages/preswald && \
    chmod -R 755 /usr/local/lib/python3.12/site-packages/preswald

RUN chown -R preswald:preswald /app

# Switch to the non-root user
USER preswald

# Copy and set up the entrypoint script
COPY --chown=preswald:preswald docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Environment variables
ENV HOST=0.0.0.0
ENV PORT=8501

# Add health check to monitor service status
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]
