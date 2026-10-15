#Requires -Version 5.1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$stage = Join-Path $root "mcpb\src"
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory $stage | Out-Null
Copy-Item (Join-Path $root "src") (Join-Path $stage "src") -Recurse
$sys = Get-Content (Join-Path $root "assets\prompts\system.md") -Raw
$usr = Get-Content (Join-Path $root "assets\prompts\user.md") -Raw
$ex = Get-Content (Join-Path $root "assets\prompts\examples.json") -Raw | ConvertFrom-Json
$sw = ($sys -split '\s+').Count; $uw = ($usr -split '\s+').Count
if ($sw -lt 3000) { throw "system.md $sw words, need >=3000" }
if ($uw -lt 4000) { throw "user.md $uw words, need >=4000" }
if ($ex.Count -lt 100) { throw "examples.json $($ex.Count), need >=100" }
Write-Host "3-4-100 OK ($sw / $uw / $($ex.Count))"
New-Item -ItemType Directory (Join-Path $root "dist") -Force | Out-Null
& C:\Users\sandr\.bun\bin\bun.exe x --yes @anthropic-ai/mcpb pack $root (Join-Path $root "dist\democraft-mcp-v0.1.1.mcpb")
