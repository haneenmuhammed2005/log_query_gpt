# Docker Helper Commands for Windows
# Author: Haneen

Write-Host "ICS-LogQueryGPT Docker Helper" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

param(
    [Parameter(Position=0)]
    [string]$Command
)

function Build {
    Write-Host "Building Docker images..." -ForegroundColor Yellow
    docker-compose -f docker/docker-compose.yml build
}

function Start {
    Write-Host "Starting services..." -ForegroundColor Yellow
    docker-compose -f docker/docker-compose.yml up -d
    Write-Host "✅ Services started!" -ForegroundColor Green
    Write-Host "Access app at: http://localhost:8501"
}

function Stop {
    Write-Host "Stopping services..." -ForegroundColor Yellow
    docker-compose -f docker/docker-compose.yml down
    Write-Host "✅ Services stopped!" -ForegroundColor Green
}

function Logs {
    Write-Host "Showing logs..." -ForegroundColor Yellow
    docker-compose -f docker/docker-compose.yml logs -f
}

function Restart {
    Write-Host "Restarting services..." -ForegroundColor Yellow
    docker-compose -f docker/docker-compose.yml restart
    Write-Host "✅ Services restarted!" -ForegroundColor Green
}

function Clean {
    Write-Host "Cleaning up..." -ForegroundColor Yellow
    docker-compose -f docker/docker-compose.yml down -v
    Write-Host "✅ Cleaned up!" -ForegroundColor Green
}

function Status {
    Write-Host "Service status:" -ForegroundColor Yellow
    docker-compose -f docker/docker-compose.yml ps
}

# Main logic
switch ($Command) {
    "build" { Build }
    "start" { Start }
    "stop" { Stop }
    "logs" { Logs }
    "restart" { Restart }
    "clean" { Clean }
    "status" { Status }
    default {
        Write-Host "Usage: .\docker\docker-commands.ps1 {build|start|stop|logs|restart|clean|status}" -ForegroundColor Red
        exit 1
    }
}