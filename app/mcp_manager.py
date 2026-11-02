import asyncio, logging, os, sys
from contextlib import AsyncExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from app.config import get_settings

logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
SERVER_MODULES = {"logs":"app.servers.logs","database":"app.servers.database","kubernetes":"app.servers.kubernetes","github":"app.servers.github"}

@dataclass(frozen=True)
class RegisteredTool:
    public_name: str
    server_name: str
    original_name: str
    description: str
    input_schema: dict[str, Any]

class MCPClientManager:
    """Own one independent stdio MCP session per configured server."""
    def __init__(self):
        self._stack = AsyncExitStack()
        self.sessions: dict[str, ClientSession] = {}
        self.tools: dict[str, RegisteredTool] = {}
        self._semaphore = asyncio.Semaphore(get_settings().agent_max_parallel_tools)

    async def connect_all(self):
        try:
            for server_name, module in SERVER_MODULES.items():
                params = StdioServerParameters(command=sys.executable, args=["-m", module], env={**os.environ, "PYTHONPATH": str(ROOT)})
                read, write = await self._stack.enter_async_context(stdio_client(params))
                session = await self._stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                self.sessions[server_name] = session
                result = await session.list_tools()
                for tool in result.tools:
                    public_name = f"{server_name}__{tool.name}"
                    if public_name in self.tools:
                        raise RuntimeError(f"Duplicate tool name: {public_name}")
                    self.tools[public_name] = RegisteredTool(public_name, server_name, tool.name, tool.description or "", tool.inputSchema or {"type":"object","properties":{}})
                logger.info("mcp_server_connected server=%s tools=%d", server_name, len(result.tools))
        except Exception:
            await self.close()
            raise

    def ollama_tools(self):
        return [{"type":"function","function":{"name":t.public_name,"description":t.description,"parameters":t.input_schema}} for t in self.tools.values()]

    async def call_tool(self, public_name: str, arguments: dict[str, Any]) -> str:
        item = self.tools.get(public_name)
        if item is None:
            raise ValueError(f"Tool is not registered: {public_name}")
        session = self.sessions.get(item.server_name)
        if session is None:
            raise RuntimeError(f"MCP server is disconnected: {item.server_name}")
        async with self._semaphore:
            result = await asyncio.wait_for(session.call_tool(item.original_name, arguments), timeout=get_settings().mcp_tool_timeout_seconds)
        chunks = [c.text if hasattr(c, "text") else str(c) for c in result.content]
        if result.isError:
            raise RuntimeError("MCP tool error: " + " ".join(chunks))
        return "\n".join(chunks)[:12000]

    async def close(self):
        await self._stack.aclose()
        self.sessions.clear()
        self.tools.clear()
