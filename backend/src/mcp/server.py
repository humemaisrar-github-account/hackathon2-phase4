"""
MCP Server for the Todo AI Chatbot.
This server exposes the todo management functions as standardized tools
that can be used by the AI model.
"""
import asyncio
from mcp.server import Server
from mcp.types import Tool
import logging

# Initialize the MCP server
server = Server("todo-ai-chatbot-mcp")

# Import all the tools
from .tools.add_task import *
from .tools.list_tasks import *
from .tools.complete_task import *
from .tools.delete_task import *
from .tools.update_task import *


# Health check endpoint
@server.check_health()
def health_check():
    return {"status": "healthy", "service": "todo-ai-chatbot-mcp"}


# Initialize the server
async def serve():
    async with server.serve():
        await asyncio.Event().wait()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())