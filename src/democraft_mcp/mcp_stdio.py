"""stdio entry (stateless server: tools run directly, no DB, no proxy needed)."""

from .server import mcp


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
