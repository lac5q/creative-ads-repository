#!/usr/bin/env python3
"""
Simple MCP Server for Docker
A basic MCP server that provides Docker-related tools and can work with socat.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List

from mcp import ClientSession, StdioServerParameters
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import subprocess
import platform
import os

# Create server instance
server = Server("docker-mcp-server")

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="docker://containers",
            name="Docker Containers",
            description="List of running Docker containers",
            mimeType="application/json",
        ),
        Resource(
            uri="docker://images",
            name="Docker Images", 
            description="List of Docker images",
            mimeType="application/json",
        ),
        Resource(
            uri="system://info",
            name="System Information",
            description="System and Docker information",
            mimeType="application/json",
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a specific resource."""
    if uri == "docker://containers":
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error getting containers: {e}"
    
    elif uri == "docker://images":
        try:
            result = subprocess.run(
                ["docker", "images", "--format", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error getting images: {e}"
    
    elif uri == "system://info":
        info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture(),
            "machine": platform.machine(),
            "hostname": platform.node(),
            "working_directory": os.getcwd()
        }
        return json.dumps(info, indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools."""
    return [
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
            name="docker_images",
            description="List Docker images",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            },
        ),
        Tool(
            name="docker_run",
            description="Run a Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "image": {
                        "type": "string",
                        "description": "Docker image to run"
                    },
                    "command": {
                        "type": "string", 
                        "description": "Command to run in container (optional)"
                    },
                    "detached": {
                        "type": "boolean",
                        "description": "Run in detached mode",
                        "default": True
                    }
                },
                "required": ["image"],
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
        ),
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
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    if name == "docker_ps":
        try:
            cmd = ["docker", "ps"]
            if arguments.get("all", False):
                cmd.append("-a")
            cmd.extend(["--format", "table {{.ID}}\t{{.Image}}\t{{.Command}}\t{{.CreatedAt}}\t{{.Status}}\t{{.Ports}}\t{{.Names}}"])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return [TextContent(type="text", text=result.stdout)]
        except subprocess.CalledProcessError as e:
            return [TextContent(type="text", text=f"Error: {e.stderr}")]
    
    elif name == "docker_images":
        try:
            result = subprocess.run(
                ["docker", "images", "--format", "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}"],
                capture_output=True,
                text=True,
                check=True
            )
            return [TextContent(type="text", text=result.stdout)]
        except subprocess.CalledProcessError as e:
            return [TextContent(type="text", text=f"Error: {e.stderr}")]
    
    elif name == "docker_run":
        try:
            cmd = ["docker", "run"]
            if arguments.get("detached", True):
                cmd.append("-d")
            cmd.append(arguments["image"])
            if "command" in arguments:
                cmd.extend(arguments["command"].split())
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return [TextContent(type="text", text=f"Container started: {result.stdout.strip()}")]
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
    
    elif name == "hello_docker":
        name_param = arguments.get("name", "Docker")
        message = f"Hello from {name_param} MCP Server! 🐳\n"
        message += f"Server is running and ready to help with Docker operations.\n"
        message += f"Available tools: docker_ps, docker_images, docker_run, system_info"
        return [TextContent(type="text", text=message)]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    # Run the server using stdio
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            StdioServerParameters(
                command="simple_mcp_server"
            )
        )

if __name__ == "__main__":
    asyncio.run(main()) 