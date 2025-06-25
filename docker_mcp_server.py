#!/usr/bin/env python3
"""
Docker MCP Server
A simple MCP server that runs in Docker and provides various tools.
"""

from fastmcp import FastMCP
import platform
import os
import subprocess
import json

# Initialize the MCP server
app = FastMCP("Docker MCP Server")

@app.tool()
def hello_docker():
    """Test tool for Docker MCP server"""
    return "Hello from Docker MCP Server! 🐳"

@app.tool()  
def system_info():
    """Get system information from Docker container"""
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "architecture": platform.architecture(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "container_id": os.environ.get("HOSTNAME", "unknown")
    }

@app.tool()
def list_environment():
    """List all environment variables in the container"""
    return dict(os.environ)

@app.tool()
def run_command(command: str):
    """Run a shell command inside the Docker container"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
    except subprocess.TimeoutExpired:
        return {
            "command": command,
            "error": "Command timed out after 30 seconds",
            "success": False
        }
    except Exception as e:
        return {
            "command": command,
            "error": str(e),
            "success": False
        }

@app.tool()
def docker_health_check():
    """Check the health status of the Docker MCP server"""
    return {
        "status": "healthy",
        "server": "Docker MCP Server",
        "version": "1.0.0",
        "uptime": "running",
        "tools_available": ["hello_docker", "system_info", "list_environment", "run_command", "docker_health_check"]
    }

if __name__ == "__main__":
    print("Starting Docker MCP Server on port 8000...")
    app.run(port=8000, host="0.0.0.0") 