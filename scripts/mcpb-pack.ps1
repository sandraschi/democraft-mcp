#Requires -Version 5.1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$stage = Join-Path $root "mcpb\src"
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory $stage | Out-Null
# Stage the PACKAGE dir, not src itself: layout must be mcpb/src/<pkg>/ so that
# `import democraft_mcp` resolves with only mcpb/src on sys.path. Copying `src`
# as a whole produced mcpb/src/src/<pkg>/ - a bundle that cannot import itself
# (H3, 2026-10-18; 2026-07-26 incident class).
Copy-Item (Join-Path $root "src\democraft_mcp") (Join-Path $stage "democraft_mcp") -Recurse
# Strip pollution the copy brings along (L2): bytecode + editor backups.
Get-ChildItem -Recurse -Path $stage -Include "__pycache__" -Directory -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Path $stage -Include "*.pyc", "*.bak", "*.bak.*" -File -ErrorAction SilentlyContinue |
    Remove-Item -Force -ErrorAction SilentlyContinue
$sys = Get-Content (Join-Path $root "assets\prompts\system.md") -Raw
$usr = Get-Content (Join-Path $root "assets\prompts\user.md") -Raw
$ex = Get-Content (Join-Path $root "assets\prompts\examples.json") -Raw | ConvertFrom-Json
$sw = ($sys -split '\s+').Count; $uw = ($usr -split '\s+').Count
if ($sw -lt 3000) { throw "system.md $sw words, need >=3000" }
if ($uw -lt 4000) { throw "user.md $uw words, need >=4000" }
if ($ex.Count -lt 100) { throw "examples.json $($ex.Count), need >=100" }
Write-Host "3-4-100 OK ($sw / $uw / $($ex.Count))"
New-Item -ItemType Directory (Join-Path $root "dist") -Force | Out-Null
$ver = (Join-Path $root "dist\democraft-mcp-v0.1.1.mcpb")
& C:\Users\sandr\.bun\bin\bun.exe x --yes @anthropic-ai/mcpb pack $root $ver
# Stable-name copy for releases/latest/download/<name>.mcpb (MCPB_PACKAGING_STANDARDS.md 2.2b).
Copy-Item $ver (Join-Path $root "dist\democraft-mcp.mcpb") -Force
Write-Host "stable: dist\democraft-mcp.mcpb"
