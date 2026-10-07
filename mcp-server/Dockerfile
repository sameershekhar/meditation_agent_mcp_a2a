FROM python:3.14-slim

WORKDIR /app

RUN pip install uv && \
    apt-get update && \
    apt-get install -y openssl && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .

RUN mkdir -p /certs

ENTRYPOINT ["/bin/sh", "-c"]
CMD ["if [ ! -f /certs/server.crt ] || [ ! -f /certs/server.key ]; then \
    echo 'Generating self-signed certificates...'; \
    openssl req -x509 -newkey rsa:4096 -nodes -out /certs/server.crt -keyout /certs/server.key -days 365 \
      -subj '/C=US/ST=State/L=City/O=Organization/CN=localhost'; \
  fi && \
  uv run python src/server.py http"]

