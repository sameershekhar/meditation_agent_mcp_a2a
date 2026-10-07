#!/bin/bash

# Generate self-signed SSL certificates for the MCP server
# This script creates a certificate valid for 365 days

CERT_DIR="./certs"
CERT_FILE="$CERT_DIR/server.crt"
KEY_FILE="$CERT_DIR/server.key"

# Create certs directory if it doesn't exist
mkdir -p "$CERT_DIR"

# Generate self-signed certificate
if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    echo "Generating self-signed SSL certificates..."

    openssl req -x509 \
        -newkey rsa:4096 \
        -nodes \
        -out "$CERT_FILE" \
        -keyout "$KEY_FILE" \
        -days 365 \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

    echo "✓ Certificates generated successfully"
    echo "  Certificate: $CERT_FILE"
    echo "  Private Key: $KEY_FILE"
else
    echo "✓ Certificates already exist"
fi
