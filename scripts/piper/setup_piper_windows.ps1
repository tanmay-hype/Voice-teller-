<#
PowerShell helper to prepare Piper for Windows users by using Docker.

What it does:
- Creates `./models` and `./media` directories
- Downloads a Piper ONNX model into `./models` (with retries)
- Brings up the `piper` container using `docker-compose.yml`
- Verifies Piper can generate a short audio sample

Usage (PowerShell as admin not required if Docker is available):
  .\scripts\setup_piper_windows.ps1
#>

Set-StrictMode -Version Latest

$ErrorActionPreference = 'Stop'

Write-Host "Preparing directories..."
$root = Split-Path -Parent $PSCommandPath
if (-not $root) { $root = Get-Location }
$models = Join-Path $root "models"
$media = Join-Path $root "media"
if (!(Test-Path $models)) { New-Item -ItemType Directory -Path $models | Out-Null }
if (!(Test-Path $media)) { New-Item -ItemType Directory -Path $media | Out-Null }

function Download-File($url, $out) {
    $max = 5
    $i = 0
    while ($i -lt $max) {
        try {
            Write-Host "Downloading $url to $out (attempt $($i+1)/$max)..."
            [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
            Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing -TimeoutSec 120
            return $true
        } catch {
            Write-Warning "Download failed: $($_.Exception.Message)"
            Start-Sleep -Seconds (5 * ($i + 1))
            $i++
        }
    }
    return $false
}

# Prefer official rhasspy piper voices release; fallback to huggingface if needed
$modelName = 'en_US-amy-medium.onnx'
$dest = Join-Path $models $modelName
$urls = @(
    "https://github.com/rhasspy/piper-voices/releases/download/v1.0.0/$modelName",
    "https://huggingface.co/rhasspy/piper/resolve/main/voices/$modelName"
)

$downloaded = $false
foreach ($u in $urls) {
    if (Download-File $u $dest) { $downloaded = $true; break }
}

if (-not $downloaded) {
    Write-Error "Failed to download model. Please download manually and place it in ./models/$modelName"
    exit 1
}

Write-Host "Bringing up Piper container via docker-compose.yml..."
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker CLI not found. Please install Docker Desktop for Windows and ensure it's running."
    exit 1
}

docker compose -f docker-compose.yml up -d piper --build

Write-Host "Waiting for Piper container to be ready..."
Start-Sleep -Seconds 3

Write-Host "Testing Piper: generating brief sample..."
$sampleOut = Join-Path $media "piper_test.wav"
try {
    $cmd = "bash -lc 'echo \"Hello from Piper\" | python -m piper --model /models/$modelName --output-file /tmp/piper_out.wav && cp /tmp/piper_out.wav /media/piper_test.wav'"
    docker exec -i piper /bin/sh -c $cmd
    if (Test-Path $sampleOut) {
        Write-Host "Success: sample generated at $sampleOut"
    } else {
        Write-Warning "Piper ran but sample not found. Check container logs: docker logs piper"
    }
} catch {
    Write-Error "Piper test failed: $($_.Exception.Message)"
}

Write-Host "Done. To use Piper from the backend in Docker mode, set environment variable PIPER_USE_DOCKER=1 and PIPER_DOCKER_CONTAINER=piper"
