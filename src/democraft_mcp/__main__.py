"""Entry point: stdio by default, FastAPI/HTTP when MCP_TRANSPORT=http.

The MCPB launch check starts `python -m democraft_mcp` with MCP_TRANSPORT=http
and probes TCP 39812; Claude Desktop uses the manifest's stdio entry point.
"""

from __future__ import annotations

import os


def main() -> None:
    transport = os.environ.get("MCP_TRANSPORT", "stdio").lower()
    if transport in ("http", "streamable-http", "sse"):
        import uvicorn

        from .server import app

        port = int(os.environ.get("PORT", "39812"))
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
        return
    from .mcp_stdio import main as run_stdio

    run_stdio()


if __name__ == "__main__":
    main()
