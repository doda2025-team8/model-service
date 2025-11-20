# Model Service - SMS Spam Classifier

A containerized microservice for SMS spam detection using machine learning.

**Team:** doda2025-team8  
**Repository:** https://github.com/doda2025-team8/model-service

## 🏗️ Architecture

- **Runtime**: Python 3.12.9
- **Framework**: Flask + Swagger UI
- **ML Stack**: scikit-learn, NLTK, Decision Tree
- **Container**: Docker (multi-arch: amd64, arm64)

**Model Loading:** Models are NOT baked into the Docker image. They download at runtime from GitHub Releases or can be mounted via volume. This allows model updates without rebuilding containers.

## 🚀 Quick Start

### Pull and Run

**Windows PowerShell:**
```powershell
docker pull ghcr.io/doda2025-team8/model-service:latest

docker run -d -p 8081:8081 `
  -e GITHUB_REPO=doda2025-team8/model-service `
  --name model-service `
  ghcr.io/doda2025-team8/model-service:latest

# Wait 30-60 seconds for model download, then test
Invoke-RestMethod http://localhost:8081/health
```

**Linux/Mac:**
```bash
docker pull ghcr.io/doda2025-team8/model-service:latest

docker run -d -p 8081:8081 \
  -e GITHUB_REPO=doda2025-team8/model-service \
  --name model-service \
  ghcr.io/doda2025-team8/model-service:latest

curl http://localhost:8081/health
```

### Faster Startup (with Volume Mount)

If you have models locally:

```powershell
# Windows
docker run -d -p 8081:8081 -v ${PWD}/output:/app/models --name model-service ghcr.io/doda2025-team8/model-service:latest

# Linux/Mac
docker run -d -p 8081:8081 -v ./output:/app/models --name model-service ghcr.io/doda2025-team8/model-service:latest
```

### Persistent Cache

```powershell
docker volume create model-cache
docker run -d -p 8081:8081 -v model-cache:/app/models -e GITHUB_REPO=doda2025-team8/model-service --name model-service ghcr.io/doda2025-team8/model-service:latest
```

## 📡 API Usage

### Health Check
```powershell
# Windows
Invoke-RestMethod http://localhost:8081/health

# Linux/Mac
curl http://localhost:8081/health
```

### Predict Spam

**Windows:**
```powershell
$body = @{ sms = "WIN FREE PRIZE NOW!" } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8081/predict -Method POST -ContentType "application/json" -Body $body
```

**Linux/Mac:**
```bash
curl -X POST http://localhost:8081/predict \
  -H "Content-Type: application/json" \
  -d '{"sms": "WIN FREE PRIZE NOW!"}'
```

**Response:**
```json
{
  "result": "spam",
  "classifier": "decision tree",
  "confidence": 0.92,
  "sms": "WIN FREE PRIZE NOW!"
}
```

**API Docs:** http://localhost:8081/apidocs

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_SERVICE_PORT` | `8081` | Service port |
| `MODEL_DIR` | `/app/models` | Model directory |
| `MODEL_VERSION` | `latest` | Model version from releases |
| `GITHUB_REPO` | `doda2025-team8/model-service` | GitHub repo for downloads |

**Examples:**

```powershell
# Custom port
docker run -d -p 9000:9000 -e MODEL_SERVICE_PORT=9000 -e GITHUB_REPO=doda2025-team8/model-service --name model-service ghcr.io/doda2025-team8/model-service:latest

# Specific version
docker run -d -p 8081:8081 -e MODEL_VERSION=v1.0.0 -e GITHUB_REPO=doda2025-team8/model-service --name model-service ghcr.io/doda2025-team8/model-service:latest
```

## 🏋️ Training Models

Models are trained via GitHub Actions:

1. Go to: https://github.com/doda2025-team8/model-service/actions
2. Run **"Train and Release Model"** workflow
3. Enter version (e.g., `v1.0.0`) and release notes
4. Workflow trains and creates GitHub release with model files
5. Use new model: `docker run -e MODEL_VERSION=v1.0.0 ...`

**Releases:** https://github.com/doda2025-team8/model-service/releases

## 🐳 Local Development

```powershell
# Build
docker build -t model-service:local .

# Run with local models
docker run -d -p 8081:8081 -v ${PWD}/output:/app/models --name test model-service:local

# Test
Invoke-RestMethod http://localhost:8081/health

# Cleanup
docker stop test && docker rm test
```

## 🛑 Container Management

```powershell
# View logs
docker logs -f model-service

# Stop
docker stop model-service

# Remove
docker rm model-service

# Stop and remove
docker rm -f model-service
```

## 🔍 Troubleshooting

**Container won't start:**
```powershell
docker logs model-service  # Check for errors
```

**Models not loading:**
```powershell
docker exec model-service ls -lh /app/models/  # Verify models exist
```

**Force model re-download:**
```powershell
docker rm -f model-service
docker volume rm model-cache  # If using cache
# Run container again
```
