<#
connect_tiktok.ps1

ช่วยสตาร์ท FastAPI callback (uvicorn) และ ngrok แล้วสร้าง TikTok authorize URL ให้
วิธีใช้: เปิด PowerShell ในโฟลเดอร์ repo แล้วรัน:
  .\scripts\connect_tiktok.ps1

ก่อนรันให้ตั้งค่า environment variables (หรือใส่เมื่อสคริปต์ถาม):
  TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET (ถ้ามี), optionally TIKTOK_AUTH_URL

หมายเหตุ: สคริปต์จะพยายามเรียก python และ ngrok จาก PATH
#>

function Import-DotEnv {
    $dot = Join-Path (Get-Location) '.env'
    if (Test-Path $dot) {
        Get-Content $dot | ForEach-Object {
            if ($_ -and $_ -notmatch '^\s*#') {
                $parts = $_ -split '=',2
                if ($parts.Count -eq 2) {
                    $k = $parts[0].Trim()
                    $v = $parts[1].Trim().Trim('"')
                    Write-Host "Loading env $k"
                    Set-Item -Path Env:$k -Value $v
                }
            }
        }
    }

}

Import-DotEnv

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "python not found in PATH. Please install Python and ensure 'python' is on PATH."; exit 1
}
if (-not (Get-Command ngrok -ErrorAction SilentlyContinue)) {
    Write-Warning "ngrok not found in PATH. Install ngrok and login (https://ngrok.com). You can still run uvicorn and set REDIRECT_URI manually.";
}

# read required values
$clientKey = $env:TIKTOK_CLIENT_KEY
if (-not $clientKey) { $clientKey = Read-Host 'Enter TIKTOK_CLIENT_KEY (client key / app id)' }
if (-not $clientKey) { Write-Error 'client key required'; exit 1 }

$clientSecret = $env:TIKTOK_CLIENT_SECRET
if (-not $clientSecret) { $clientSecret = Read-Host -AsSecureString 'Enter TIKTOK_CLIENT_SECRET (press Enter if none)'; $clientSecret = [Runtime.InteropServices.Marshal]::PtrToStringUni([Runtime.InteropServices.Marshal]::SecureStringToBSTR($clientSecret)) }

# uvicorn port
$port = 8080

Write-Host "Starting uvicorn (FastAPI callback) on port $port..."
$uvicornArgs = "-m uvicorn src.tiktok_oauth_callback:app --host 0.0.0.0 --port $port"
$uvicornProc = Start-Process -FilePath python -ArgumentList $uvicornArgs -WindowStyle Minimized -PassThru
Write-Host "uvicorn started (PID $($uvicornProc.Id)). Give it a moment to boot..."

if (Get-Command ngrok -ErrorAction SilentlyContinue) {
    Write-Host "Starting ngrok http $port ..."
    $ngrokProc = Start-Process -FilePath ngrok -ArgumentList "http $port" -WindowStyle Minimized -PassThru
    Write-Host "ngrok started (PID $($ngrokProc.Id)). Waiting for tunnel to appear..."

    # poll ngrok API for public URL
    $publicUrl = $null
    for ($i=0; $i -lt 60; $i++) {
        try {
            $t = Invoke-RestMethod -Uri 'http://127.0.0.1:4040/api/tunnels' -UseBasicParsing -ErrorAction Stop
            if ($t.tunnels) {
                foreach ($tun in $t.tunnels) {
                    if ($tun.public_url -and $tun.public_url -match '^https://') { $publicUrl = $tun.public_url; break }
                }
            }
        } catch { }
        if ($publicUrl) { break }
        Start-Sleep -Seconds 1
    }
    if (-not $publicUrl) { Write-Warning 'Could not detect ngrok public URL via http://127.0.0.1:4040. Please copy the HTTPS Forwarding URL from ngrok UI and set REDIRECT_URI in the TikTok console.' }
} else {
    $publicUrl = $null
}

if ($publicUrl) {
    Write-Host "Detected public URL: $publicUrl"
    $redirect = "$publicUrl/tiktok/callback"
    Write-Host "Using redirect URI: $redirect"
    Write-Host "Ensure the TikTok app (in your Developer console) has this Redirect URI configured."
} else {
    $redirect = Read-Host 'Enter REDIRECT_URI you configured in TikTok developer console (e.g. https://your-ngrok-id.ngrok-free.app/tiktok/callback)'
}

$authBase = $env:TIKTOK_AUTH_URL
if (-not $authBase) { $authBase = 'https://www.tiktok.com/v2/auth/authorize/' }
$scope = 'user.info.basic,video.upload'
$encodedRedirect = [System.Uri]::EscapeDataString($redirect)
$state = [System.Guid]::NewGuid().ToString()
$authUrl = "$authBase?client_key=$clientKey&response_type=code&scope=$scope&redirect_uri=$encodedRedirect&state=$state"

Write-Host "Authorize URL:\n$authUrl`n"

$open = Read-Host 'Open authorize URL in your browser now? (Y/n)'
if ($open -eq '' -or $open -match '^[Yy]') {
    Start-Process $authUrl
    Write-Host 'Browser opened. Complete the OAuth consent. The callback endpoint will exchange the code automatically.'
} else {
    Write-Host 'Open the URL above manually in your browser to continue.'
}

Write-Host 'Now waiting for tokens to be persisted by the callback. This will poll the local token loader for up to 300s.'

$outputDir = $env:OUTPUT_DIR
if (-not $outputDir) { $outputDir = Join-Path (Get-Location) 'output' }

for ($i=0; $i -lt 60; $i++) {
    try {
        $tmp = [System.IO.Path]::GetTempFileName()
        $py = @"
from src import token_store
try:
    t = token_store.load_tokens()
    print('TOKENS_FOUND')
    print(t)
except Exception:
    pass
"@
        Set-Content -Path $tmp -Value $py -Encoding UTF8
        $res = & python $tmp 2>$null
        Remove-Item $tmp -ErrorAction SilentlyContinue
        if ($res -and $res -match 'TOKENS_FOUND') {
            Write-Host 'Tokens persisted by callback. You can now run the runner in dry-run or real-run.'
            break
        }
    } catch {
        # ignore
    }
    Start-Sleep -Seconds 5
}

Write-Host "If tokens were not found, check the uvicorn logs and ensure the callback received the redirect. Token storage is handled by src/token_store.py"
Write-Host "To run a dry-run post: python -m src.runner --dry-run"
