#!/usr/bin/env python3
"""
Example MCP client for connecting to the HTTPS remote MCP server.

This demonstrates how to connect to the MCP server over HTTPS.
"""

import ssl
import asyncio
import httpx
from mcp import ClientSession
from mcp.client.http import HttpClientTransport


async def connect_to_mcp_server(server_url: str, verify_ssl: bool = False):
    """
    Connect to the remote MCP server over HTTPS.

    Args:
        server_url: URL of the MCP server (e.g., https://localhost:8000)
        verify_ssl: Whether to verify SSL certificate (set False for self-signed)
    """

    # Configure SSL context for self-signed certificates
    if not verify_ssl:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
    else:
        ssl_context = None

    # Create HTTP client with SSL configuration
    async with httpx.AsyncClient(verify=verify_ssl) as http_client:
        # Create HTTP transport for MCP
        transport = HttpClientTransport(
            client=http_client,
            url=f"{server_url}/mcp"
        )

        # Create MCP session
        async with ClientSession(transport) as session:
            # Initialize connection
            await session.initialize()

            # Get available resources
            resources = await session.list_resources()
            print(f"Available resources: {resources}")

            # Get available tools
            tools = await session.list_tools()
            print(f"Available tools: {tools}")

            # Get available prompts
            prompts = await session.list_prompts()
            print(f"Available prompts: {prompts}")


async def main():
    """Main entry point."""

    # Server configuration
    server_url = "https://localhost:8000"
    verify_ssl = False  # Set to True for production with real certificates

    try:
        await connect_to_mcp_server(server_url, verify_ssl=verify_ssl)
        print("✓ Successfully connected to MCP server")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
