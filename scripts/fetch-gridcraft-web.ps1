# Fetch the GridCraft web build into the democraft webapp's public folder.
# The wasm bundle is generated, gitignored, and required by /studio.
param([string]$Version = "0.9.0")

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$temp = Join-Path $env:TEMP "gridcraft-web-$Version"
$zip = Join-Path $temp "gridcraft-web-$Version.zip"
$dest = Join-Path $root "web_sota\public\gridcraft-web"

New-Item -ItemType Directory -Force -Path $temp | Out-Null
gh release download "v$Version" -R storytold/gridcraft -p "gridcraft-web-$Version.zip" -D $temp --clobber
Expand-Archive -Path $zip -DestinationPath $temp -Force

if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
Copy-Item (Join-Path $temp "gridcraft-web-$Version") $dest -Recurse
Write-Host "GridCraft web $Version -> $dest"
