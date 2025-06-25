#!/usr/bin/env python3
"""
TCP MCP Server for Docker
A TCP-based MCP server that works with socat configuration.
"""

import asyncio
import json
import sys
import socket
from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
)
import subprocess
import platform
import os

# Create server instance
server = Server("docker-mcp-server")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="hello_docker",
            description="Simple hello world test for Docker MCP server",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name to greet",
                        "default": "Docker"
                    }
                },
                "additionalProperties": False
            },
        ),
        Tool(
            name="docker_ps",
            description="List running Docker containers",
            inputSchema={
                "type": "object",
                "properties": {
                    "all": {
                        "type": "boolean",
                        "description": "Show all containers (default: only running)",
                        "default": False
                    }
                },
                "additionalProperties": False
            },
        ),
        Tool(
            name="system_info",
            description="Get system information",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    if name == "hello_docker":
        name_param = arguments.get("name", "Docker")
        message = f"Hello from {name_param} MCP Server! 🐳\n"
        message += f"Server is running on TCP and ready to help with Docker operations.\n"
        message += f"Available tools: hello_docker, docker_ps, system_info"
        return [TextContent(type="text", text=message)]
    
    elif name == "docker_ps":
        try:
            cmd = ["docker", "ps"]
            if arguments.get("all", False):
                cmd.append("-a")
            cmd.extend(["--format", "table {{.ID}}\t{{.Image}}\t{{.Command}}\t{{.CreatedAt}}\t{{.Status}}\t{{.Ports}}\t{{.Names}}"])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return [TextContent(type="text", text=result.stdout)]
        except subprocess.CalledProcessError as e:
            return [TextContent(type="text", text=f"Error: {e.stderr}")]
    
    elif name == "system_info":
        info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture(),
            "machine": platform.machine(),
            "hostname": platform.node(),
            "working_directory": os.getcwd(),
            "docker_version": "Unknown"
        }
        
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True, check=True)
            info["docker_version"] = result.stdout.strip()
        except subprocess.CalledProcessError:
            pass
            
        return [TextContent(type="text", text=json.dumps(info, indent=2))]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def handle_client(reader, writer):
    """Handle individual client connections."""
    try:
        # Read incoming data
        while True:
            data = await reader.read(8192)
            if not data:
                break
            
            # Parse JSON-RPC message
            try:
                message = json.loads(data.decode())
                print(f"Received: {message}", file=sys.stderr)
                
                # Simple response for now
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": {
                        "message": "Hello from Docker MCP Server!",
                        "tools": ["hello_docker", "docker_ps", "system_info"]
                    }
                }
                
                response_data = json.dumps(response).encode() + b'\n'
                writer.write(response_data)
                await writer.drain()
                
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}", file=sys.stderr)
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32700, "message": "Parse error"},
                    "id": None
                }
                writer.write(json.dumps(error_response).encode() + b'\n')
                await writer.drain()
                
    except Exception as e:
        print(f"Client error: {e}", file=sys.stderr)
    finally:
        writer.close()
        await writer.wait_closed()

async def start_server():
    """Start the TCP server."""
    server_instance = await asyncio.start_server(
        handle_client, 
        'localhost', 
        8811
    )
    
    addr = server_instance.sockets[0].getsockname()
    print(f'Docker MCP Server serving on {addr[0]}:{addr[1]}', file=sys.stderr)
    
    async with server_instance:
        await server_instance.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("Server stopped", file=sys.stderr) 