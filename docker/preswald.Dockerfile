FROM python:3.12-slim-bullseye as builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Define an argument to check if we should use local wheel
ARG USE_LOCAL_WHEEL=false
COPY wheel.whl /app/wheel.whl

RUN pip install --no-cache-dir --upgrade pip

# Install using the appropriate method
RUN if [ "$USE_LOCAL_WHEEL" = "true" ] && [ -f /app/wheel.whl ]; then \
    echo "Installing from local wheel" && \
    pip install --no-cache-dir --upgrade /app/wheel.whl --force-reinstall; \
    else \
    echo "Installing from PyPI" && \
    pip install --no-cache-dir --upgrade preswald; \
    fi

FROM python:3.12-slim-bullseye

WORKDIR /app

RUN useradd -m -u 1000 preswald

COPY --from=builder /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/
COPY --from=builder /usr/local/bin/preswald /usr/local/bin/
RUN chown -R preswald:preswald /usr/local/lib/python3.12/site-packages/preswald && \
    chmod -R 755 /usr/local/lib/python3.12/site-packages/preswald

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN chown -R preswald:preswald /app

USER preswald

COPY --chown=preswald:preswald entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV HOST=0.0.0.0
ENV PORT=8501

ENTRYPOINT ["/entrypoint.sh"]
