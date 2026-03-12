# super_nanobot Docker Deploy Script (Windows)

Write-Host "Starting super_nanobot deployment..." -ForegroundColor Green

# Check Docker
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker not installed, please install Docker first" -ForegroundColor Red
    exit 1
}

# Create config directory
$configDir = "$env:USERPROFILE\.nanobot"
if (!(Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    Write-Host "Created config directory: $configDir" -ForegroundColor Green
}

# Check config file
$configFile = "$configDir\config.json"
if (!(Test-Path $configFile)) {
    Write-Host "Config file not found, creating default config..." -ForegroundColor Yellow
    $defaultConfig = @'
{
  "providers": {
    "ollama": {
      "apiKey": "dummy",
      "apiBase": "http://host.docker.internal:11434",
      "defaultModel": "qwen3.5:4b",
      "smallModelMode": true,
      "smallModelConfig": {
        "temperature": 0.7,
        "topP": 0.9,
        "topK": 40,
        "repeatPenalty": 1.1,
        "numCtx": 8192,
        "maxTokens": 2048
      }
    }
  },
  "agents": {
    "defaults": {
      "model": "ollama/qwen3.5:4b",
      "provider": "ollama",
      "skills": ["enhanced_search", "graphrag"]
    }
  },
  "tools": {
    "enhanced_search": {
      "searxngUrl": "http://localhost:8080"
    }
  }
}
'@
    $defaultConfig | Out-File -FilePath $configFile -Encoding UTF8
    Write-Host "Default config created: $configFile" -ForegroundColor Green
    Write-Host "Please modify the config file to add your API keys" -ForegroundColor Yellow
}

# Check if Docker image exists
$imageExists = docker images super_nanobot:latest -q 2>$null
if (!$imageExists) {
    Write-Host "Building Docker image..." -ForegroundColor Cyan
    docker build -t super_nanobot:latest .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker build failed" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Docker image exists, skipping build" -ForegroundColor Green
}

# Check if container exists
$containerExists = docker ps -a --filter "name=super_nanobot" -q 2>$null
if ($containerExists) {
    Write-Host "Stopping and removing old container..." -ForegroundColor Yellow
    docker stop super_nanobot 2>$null | Out-Null
    docker rm super_nanobot 2>$null | Out-Null
}

# Run container
Write-Host "Starting super_nanobot..." -ForegroundColor Green
docker run -d `
    --name super_nanobot `
    --restart unless-stopped `
    -p 18790:18790 `
    -v "$($configDir):/root/.nanobot" `
    -e NANOBOT_CONFIG_DIR=/root/.nanobot `
    super_nanobot:latest gateway

if ($LASTEXITCODE -eq 0) {
    Write-Host "super_nanobot started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Common commands:" -ForegroundColor Cyan
    Write-Host "  View logs: docker logs -f super_nanobot"
    Write-Host "  Stop: docker stop super_nanobot"
    Write-Host "  Start: docker start super_nanobot"
    Write-Host "  Restart: docker restart super_nanobot"
    Write-Host "  Enter container: docker exec -it super_nanobot bash"
    Write-Host ""
    Write-Host "Gateway URL: http://localhost:18790" -ForegroundColor Green
} else {
    Write-Host "Failed to start" -ForegroundColor Red
}
