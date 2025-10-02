<#
Rotate TikTok client secret locally:

Usage (PowerShell):
  .\scripts\rotate_tiktok_secret.ps1 -ClientKey AWD551S8FF0G2R8N -NewSecret 'NEWSECRETVALUE'

This writes/updates .env in repo root with TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET and
removes local encrypted token store `.tokens.enc` to force re-auth.
#>
param(
    [Parameter(Mandatory=$true)] [string]$ClientKey,
    [Parameter(Mandatory=$true)] [string]$NewSecret
)

$root = Get-Location
$envFile = Join-Path $root '.env'

Write-Host "Updating .env at $envFile"

$lines = @()
if (Test-Path $envFile) {
    $lines = Get-Content $envFile
}

function set-or-add([string]$key, [string]$val) {
    $found = $false
    for ($i=0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match "^$key=") { $lines[$i] = "$key=$val"; $found = $true; break }
    }
    if (-not $found) { $lines += "$key=$val" }
}

set-or-add 'TIKTOK_CLIENT_KEY' $ClientKey
set-or-add 'TIKTOK_CLIENT_SECRET' $NewSecret

Set-Content -Path $envFile -Value $lines -Encoding UTF8
Write-Host '.env updated.'

# Remove local token store to force re-auth
$tokenPath = Join-Path $root '.tokens.enc'
if (Test-Path $tokenPath) { Remove-Item $tokenPath -Force; Write-Host 'Removed local token store (.tokens.enc)'; }
else { Write-Host 'No local token store found at .tokens.enc' }

Write-Host 'Now go to TikTok Developer Console and update server-side secret. Then re-run the connect flow to re-authorize.'
