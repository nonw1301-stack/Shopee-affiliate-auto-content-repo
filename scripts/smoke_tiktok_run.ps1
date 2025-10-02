# Smoke test runner helper for PowerShell
# Usage: ./scripts/smoke_tiktok_run.ps1 -DryRun (default) or -RunReal -Video <path> -Title <title>
param(
    [switch]$DryRun = $true,
    [switch]$RunReal = $false,
    [string]$Video = "sample.mp4",
    [string]$Title = "Smoke Test Upload"
)

if ($RunReal) { $DryRun = $false }

Write-Host "Running TikTok smoke test. DryRun=$DryRun, RunReal=$RunReal"

# Ensure Python environment
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found in PATH. Activate your virtualenv or install Python 3.11+."
    exit 1
}

# Run the smoke runner script
$script = Join-Path -Path (Get-Location) -ChildPath 'scripts\smoke_tiktok.py'
$args = @()
if ($DryRun) { $args += '--dry-run' }
if ($RunReal) { $args += '--run-real' }
if ($Video) { $args += '--video'; $args += $Video }
if ($Title) { $args += '--title'; $args += $Title }

python $script @args
