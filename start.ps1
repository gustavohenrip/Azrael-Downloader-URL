#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BackendDir = Join-Path $RootDir 'backend'
$FrontendDir = Join-Path $RootDir 'frontend'
$LogDir = Join-Path $env:LOCALAPPDATA 'AzraelDownloader\logs'
$BackendLog = Join-Path $LogDir 'backend.log'
$FrontendLog = Join-Path $LogDir 'frontend.log'

function Install-WingetPkg($id) {
    Write-Host "Installing $id via winget..."
    winget install --id $id --silent --accept-package-agreements --accept-source-agreements
}

function Ensure-Command($cmd, $wingetId) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Install-WingetPkg $wingetId
        $env:PATH = [System.Environment]::GetEnvironmentVariable('PATH', 'Machine') + ';' + [System.Environment]::GetEnvironmentVariable('PATH', 'User')
    }
}

Ensure-Command 'java'    'Microsoft.OpenJDK.21'
Ensure-Command 'mvn'     'Apache.Maven'
Ensure-Command 'node'    'OpenJS.NodeJS.LTS'
Ensure-Command 'yt-dlp'  'yt-dlp.yt-dlp'
Ensure-Command 'ffmpeg'  'Gyan.FFmpeg'

if (-not (Test-Path $BackendDir) -or -not (Test-Path $FrontendDir)) {
    Write-Error "Project folders not found."
    exit 1
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
Set-Content -Path $BackendLog -Value ''
Set-Content -Path $FrontendLog -Value ''

Write-Host "Starting backend..."
$BackendProc = Start-Process -FilePath 'mvn' -ArgumentList '-q', 'spring-boot:run' -WorkingDirectory $BackendDir -RedirectStandardOutput $BackendLog -RedirectStandardError $BackendLog -PassThru -WindowStyle Hidden

Write-Host "Waiting for backend to be ready..."
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8080/api/system/dependencies' -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch {}
    if ($BackendProc.HasExited) {
        Write-Error "Backend crashed. Check $BackendLog"
        exit 1
    }
    Start-Sleep -Seconds 2
}
if ($ready) { Write-Host "Backend ready." }

Set-Location $FrontendDir

if (-not (Test-Path 'node_modules')) {
    Write-Host "Installing frontend dependencies..."
    npm ci
}

Write-Host "Starting frontend..."
$FrontendProc = Start-Process -FilePath 'npm' -ArgumentList 'start' -WorkingDirectory $FrontendDir -RedirectStandardOutput $FrontendLog -RedirectStandardError $FrontendLog -PassThru -WindowStyle Hidden

Write-Host "Waiting for frontend to be ready..."
for ($i = 0; $i -lt 30; $i++) {
    try {
        $r = Invoke-WebRequest -Uri 'http://localhost:4200' -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($r.StatusCode -eq 200) { break }
    } catch {}
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "Backend:  http://127.0.0.1:8080"
Write-Host "Frontend: http://localhost:4200"
Write-Host "Logs:     $LogDir"
Write-Host "Press Ctrl+C to stop both services."
Write-Host ""

Start-Process 'http://localhost:4200'

try {
    while ($true) { Start-Sleep -Seconds 5 }
} finally {
    if (-not $BackendProc.HasExited)  { $BackendProc.Kill() }
    if (-not $FrontendProc.HasExited) { $FrontendProc.Kill() }
}
