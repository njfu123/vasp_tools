# Copy ai-dv-tools bundle to D:\work\tools (dv-tools + docs as siblings).
# Run from the ai-dv-tools directory (clone or unzipped tree).
# Usage:
#   .\install-to-D-work-tools.ps1
#   .\install-to-D-work-tools.ps1 -TargetRoot "D:\work\tools"

param(
    [string]$TargetRoot = "D:\work\tools"
)

$ErrorActionPreference = "Stop"

function Ensure-Dir([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Force -Path $Path | Out-Null
    }
}

$BundleRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Test-Path (Join-Path $BundleRoot "dv-tools"))) {
    Write-Error "Run this script from the ai-dv-tools folder (expected dv-tools\ alongside this script)."
}

Ensure-Dir $TargetRoot

foreach ($name in @("dv-tools", "docs")) {
    $src = Join-Path $BundleRoot $name
    if (-not (Test-Path -LiteralPath $src)) { continue }
    $dst = Join-Path $TargetRoot $name
    if (Test-Path -LiteralPath $dst) {
        Write-Host "Removing existing $dst ..."
        Remove-Item -LiteralPath $dst -Recurse -Force
    }
    Write-Host "Copying $name -> $dst"
    Copy-Item -LiteralPath $src -Destination $dst -Recurse -Force
}

Copy-Item -LiteralPath $MyInvocation.MyCommand.Path -Destination (Join-Path $TargetRoot "install-to-D-work-tools.ps1") -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Done. Installed to: $TargetRoot"
Write-Host "  $TargetRoot\dv-tools"
Write-Host "  $TargetRoot\docs"
Write-Host ""
Write-Host "Next:"
Write-Host "  cd $TargetRoot\dv-tools"
Write-Host "  py -3 -m venv .venv"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  pip install -e `".[dev]`""