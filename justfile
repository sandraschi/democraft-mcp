set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

UV := "C:\\Users\\sandr\\.local\\bin\\uv.exe"

serve:
    {{UV}} sync --extra dev
    {{UV}} run python -m democraft_mcp.server

test:
    {{UV}} run pytest -q

lint:
    {{UV}} run ruff check .
    {{UV}} run ruff format --check .

fmt:
    {{UV}} run ruff check . --fix
    {{UV}} run ruff format .

web-install:
    cd web_sota; C:\Users\sandr\.bun\bin\bun.exe install

web-build:
    cd web_sota; C:\Users\sandr\.bun\bin\bun.exe run build

web-check:
    cd web_sota; C:\Users\sandr\.bun\bin\bun.exe run check

e2e:
    cd web_sota; C:\Users\sandr\.bun\bin\bun.exe run e2e

mcpb-pack:
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/mcpb-pack.ps1

bootstrap:
    {{UV}} sync --extra dev
    pre-commit install
    cd web_sota; C:\Users\sandr\.bun\bin\bun.exe install

ci: lint test web-check web-build
    @echo "ci green."
