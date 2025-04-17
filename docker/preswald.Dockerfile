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

# COPY ./preswald-0.1.52-py3-none-any.whl /app/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --upgrade preswald
	# pip install --no-cache-dir --upgrade ./preswald-0.1.52-py3-none-any.whl --force-reinstall

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
