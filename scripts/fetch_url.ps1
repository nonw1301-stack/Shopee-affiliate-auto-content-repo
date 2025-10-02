param(
    [Parameter(Mandatory=$true)]
    [string]$Url,
    [int]$MaxBodyChars = 2000
)

Write-Host "Fetching URL: $Url" -ForegroundColor Cyan

try {
    $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 30 -ErrorAction Stop
} catch {
    Write-Host "Request failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $status = $_.Exception.Response.StatusCode.value__
        Write-Host "HTTP status: $status" -ForegroundColor Yellow
    }
    exit 2
}

$statusCode = $resp.StatusCode
Write-Host "HTTP status:" $statusCode -ForegroundColor Green

Write-Host "\n--- Response headers ---" -ForegroundColor Gray
$resp.Headers.GetEnumerator() | ForEach-Object { Write-Host ("{0}: {1}" -f $_.Name, $_.Value) }

Write-Host "\n--- Response body (first $MaxBodyChars chars) ---" -ForegroundColor Gray
$body = $resp.Content
if ($null -eq $body) { $body = $resp.RawContent } 
$safeBody = $body.ToString()
if ($safeBody.Length -gt $MaxBodyChars) { $safeBody = $safeBody.Substring(0, $MaxBodyChars) + "\n...TRUNCATED..." }
Write-Host $safeBody

Write-Host "\n(If you need the full body saved to a file, re-run with: `.\scripts\fetch_url.ps1 -Url <URL> | Out-File full_response.txt`)" -ForegroundColor DarkGray
