"""Verify the /mcp mount against the live backend (in-memory transports bypass mount bugs)."""

import asyncio
import sys

from fastmcp import Client


async def main() -> int:
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:11246/mcp"
    async with Client(url) as client:
        tools = await client.list_tools()
        names = sorted(t.name for t in tools)
        print("tools:", names)
        assert "craft" in names, "craft tool missing over HTTP"
        res = await client.call_tool("craft", {"operation": "list_apps"})
        print("list_apps ok")
        assert len(res.content) > 0
        print("MCP-HTTP-OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
