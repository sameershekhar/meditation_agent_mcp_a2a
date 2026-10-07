# HTTPS Remote MCP Server Setup

This guide explains how to run your MCP server as an HTTPS remote server using fastMCP.

## Architecture

The setup uses:
- **fastMCP**: Lightweight HTTP/HTTPS server wrapper for MCP
- **Self-signed SSL certificates**: For secure HTTPS communication
- **Docker**: For containerized deployment
- **PostgreSQL**: Backend database

## Quick Start

### 1. Generate SSL Certificates

For development/testing with self-signed certificates:

```bash
# Linux/macOS
bash generate-certs.sh

# Windows PowerShell
openssl req -x509 -newkey rsa:4096 -nodes -out certs/server.crt -keyout certs/server.key -days 365 -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

This creates:
- `certs/server.crt` - SSL certificate
- `certs/server.key` - Private key

### 2. Start with Docker Compose

```bash
docker-compose up -d
```

The MCP server will:
1. Generate certificates if they don't exist
2. Start on HTTPS (port 8000)
3. Connect to PostgreSQL

### 3. Verify It's Running

```bash
# Check container is running
docker-compose ps

# View logs
docker-compose logs mcp-server

# Health check (accepts self-signed cert)
curl -k https://localhost:8000/health
```

## Configuration

### Environment Variables

Set in `docker-compose.yml`:

- `MCP_HOST` - Server host (default: 0.0.0.0)
- `MCP_PORT` - Server port (default: 8000)
- `SSL_CERTFILE` - Path to certificate file
- `SSL_KEYFILE` - Path to private key file
- `DB_HOST` - PostgreSQL host
- `DB_PORT` - PostgreSQL port
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password

### Running Locally (without Docker)

```bash
# Install dependencies
uv sync

# Generate certificates
bash generate-certs.sh

# Run HTTP mode
uv run python src/server.py http
```

Server will start on `https://localhost:8000`

## Production Deployment

For production with real SSL certificates:

### 1. Obtain Real Certificates

Use Let's Encrypt (free) or your certificate authority:

```bash
# Using certbot (Let's Encrypt)
certbot certonly --standalone -d your-domain.com
```

### 2. Update Docker Volume

In `docker-compose.yml`, mount your certificate paths:

```yaml
volumes:
  - /etc/letsencrypt/live/your-domain.com/fullchain.pem:/certs/server.crt:ro
  - /etc/letsencrypt/live/your-domain.com/privkey.pem:/certs/server.key:ro
```

### 3. Set Port to 443

Update environment:
```yaml
environment:
  MCP_PORT: 443
```

Update port mapping:
```yaml
ports:
  - "443:8000"
```

## Client Configuration

### Claude Code MCP Configuration

Add to your `claude.config.json`:

```json
{
  "mcpServers": {
    "user-preferences": {
      "command": "curl",
      "args": ["--cacert", "/path/to/server.crt", "https://your-server:8000/mcp"],
      "disabled": false
    }
  }
}
```

Or use HTTP transport over stdio (recommended):

```json
{
  "mcpServers": {
    "user-preferences": {
      "command": "python",
      "args": ["-m", "mcp_client", "https://your-server:8000"],
      "disabled": false
    }
  }
}
```

### Curl Example

```bash
# Health check (ignoring self-signed cert)
curl -k https://localhost:8000/health

# With certificate verification (production)
curl --cacert certs/server.crt https://your-domain.com:8000/health
```

## Certificate Management

### Viewing Certificate Info

```bash
openssl x509 -in certs/server.crt -text -noout
```

### Renewing Self-Signed Certificates

```bash
# Remove old certificates
rm -rf certs/

# Generate new ones
bash generate-certs.sh

# Restart container
docker-compose restart mcp-server
```

### Converting Between Formats

```bash
# PEM to PKCS12
openssl pkcs12 -export -in server.crt -inkey server.key -out server.p12

# PKCS12 to PEM
openssl pkcs12 -in server.p12 -out server.pem -nodes
```

## Troubleshooting

### Certificate Not Found

```bash
# Check if certificates exist
ls -la certs/

# Generate if missing
bash generate-certs.sh
```

### Port Already in Use

```bash
# Find process using port 8000 (Linux/macOS)
lsof -i :8000

# Kill it
kill -9 <PID>

# Or change port in docker-compose.yml
```

### SSL Connection Errors

```bash
# Check certificate expiry
openssl x509 -in certs/server.crt -noout -dates

# Regenerate if expired
bash generate-certs.sh
docker-compose restart mcp-server
```

### Container Won't Start

```bash
# View detailed logs
docker-compose logs mcp-server -f

# Check environment variables
docker-compose config | grep -A 20 mcp-server
```

## Security Notes

⚠️ **Self-signed certificates** are suitable only for:
- Local development
- Internal networks
- Testing environments

✅ **For production**, use:
- Real SSL certificates (Let's Encrypt, paid CA)
- Proper firewall rules
- Network-level authentication
- Regular certificate updates

## Next Steps

1. ✓ Set up HTTPS server
2. Configure client to connect
3. Deploy to production infrastructure
4. Set up certificate renewal automation
5. Monitor server health and logs

## Additional Resources

- [fastMCP Documentation](https://github.com/jlouis/fastmcp)
- [OpenSSL Documentation](https://www.openssl.org/docs/)
- [Let's Encrypt Guide](https://letsencrypt.org/getting-started/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
