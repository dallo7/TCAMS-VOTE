param(
    [int]$Port = 8091
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Set-Location $ProjectRoot

foreach ($conn in Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue) {
    if ($conn.OwningProcess -and $conn.OwningProcess -ne 0) {
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

Start-Sleep -Seconds 1
& "$ProjectRoot\.venv\Scripts\uvicorn.exe" app:app --host 0.0.0.0 --port $Port
