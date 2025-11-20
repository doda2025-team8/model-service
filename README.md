# Model Service - SMS Spam Classifier

A containerized microservice for SMS spam detection using machine learning. Part of the REMLA course project.

**Team:** doda2025-team8  
**Repository:** https://github.com/doda2025-team8/model-service

## 🏗️ Architecture

- **Language**: Python 3.12.9
- **Framework**: Flask + Flasgger (Swagger UI)
- **ML Stack**: scikit-learn, NLTK
- **Container**: Docker (multi-architecture: amd64, arm64)

## 🚀 Quick Start

### Option 1: Run with Docker (Recommended)

**Windows PowerShell:**
```powershell
# Pull the latest image
docker pull ghcr.io/doda2025-team8/model-service:latest

# Run with auto-download (models download from GitHub releases)
docker run -d -p 8081:8081 `
  -e GITHUB_REPO=doda2025-team8/model-service `
  --name model-service `
  ghcr.io/doda2025-team8/model-service:latest

# Check logs
docker logs -f model-service

# Test it
Start-Sleep -Seconds 30
curl http://localhost:8081/health

# Test a prediction
$body = @{
    sms = "Congratulations! You've won a free iPhone. Click here to claim."
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8081/predict -Method Post -Body $body -ContentType "application/json"

# Stop and remove the container:
docker stop model-service
docker rm model-service
```

**Linux/Mac:**
```bash
docker pull ghcr.io/doda2025-team8/model-service:latest

docker run -d -p 8081:8081 \
  -e GITHUB_REPO=doda2025-team8/model-service \
  --name model-service \
  ghcr.io/doda2025-team8/model-service:latest

docker logs -f model-service
```

### Option 2: Run with Pre-trained Models (Volume Mount)

**Windows PowerShell:**
```powershell
# Train models locally first
python get_data.py
python src/text_preprocessing.py
python src/text_classification.py

# Run with mounted models
docker run -d -p 8081:8081 `
  -v ${PWD}/output:/app/models `
  --name model-service `
  ghcr.io/doda2025-team8/model-service:latest

# Test
curl http://localhost:8081/health
```

**Linux/Mac:**
```bash
docker run -d -p 8081:8081 \
  -v ./output:/app/models \
  --name model-service \
  ghcr.io/doda2025-team8/model-service:latest
```

## 📡 API Usage

### Health Check
**Windows PowerShell:**
```powershell
Invoke-RestMethod -Uri http://localhost:8081/health
```

**Linux/Mac/Git Bash:**
```bash
curl http://localhost:8081/health
```

### Predict SMS Spam
**Windows PowerShell:**
```powershell
$body = @{
    sms = "Congratulations! You won $1000. Click here now!"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8081/predict `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

**Linux/Mac/Git Bash:**
```bash
curl -X POST http://localhost:8081/predict \
  -H "Content-Type: application/json" \
  -d '{"sms": "Congratulations! You won $1000. Click here now!"}'
```

**Response:**
```json
{
  "sms": "Congratulations! You won $1000. Click here now!",
  "result": "spam",
  "classifier": "decision tree",
  "confidence": 0.9234
}
```

### API Documentation
Visit: `http://localhost:8081/apidocs`

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_SERVICE_PORT` | `8081` | Port the service listens on |
| `MODEL_DIR` | `/app/models` | Directory for model files |
| `MODEL_VERSION` | `latest` | Model version to download from GitHub releases |
| `GITHUB_REPO` | `doda2025-team8/model-service` | GitHub repository for model downloads |

### Examples

**Custom port (Windows):**
```powershell
docker run -d -p 9000:9000 `
  -e MODEL_SERVICE_PORT=9000 `
  -e GITHUB_REPO=doda2025-team8/model-service `
  --name model-service-9000 `
  ghcr.io/doda2025-team8/model-service:latest
```

**Specific model version (Windows):**
```powershell
docker run -d -p 8081:8081 `
  -e MODEL_VERSION=v1.0.0 `
  -e GITHUB_REPO=doda2025-team8/model-service `
  --name model-service `
  ghcr.io/doda2025-team8/model-service:latest
```

**With persistent cache (Windows):**
```powershell
# Create volume
docker volume create model-cache

# Run with cache
docker run -d -p 8081:8081 `
  -v model-cache:/app/models `
  -e GITHUB_REPO=doda2025-team8/model-service `
  --name model-service `
  ghcr.io/doda2025-team8/model-service:latest
```

## 🏋️ Training New Models

Models are trained and released automatically using GitHub Actions:

1. Go to **Actions** tab: https://github.com/doda2025-team8/model-service/actions
2. Select **"Train and Release Model"** workflow
3. Click **"Run workflow"**
4. Enter:
   - **Version**: `v1.0.0` (follow semantic versioning)
   - **Release notes**: Description of changes
5. Click **"Run workflow"**
6. Wait 2-5 minutes for completion
7. Workflow will:
   - Download SMS spam dataset
   - Preprocess text data
   - Train decision tree classifier
   - Create GitHub release
   - Attach model files (`model.joblib`, `preprocessor.joblib`)

**View releases:** https://github.com/doda2025-team8/model-service/releases

## 🐳 Building the Docker Image

### Single Architecture (for testing)

**Windows PowerShell:**
```powershell
# Build
docker build -t model-service:local .

# Run
docker run -d -p 8081:8081 `
  -v ${PWD}/output:/app/models `
  --name test `
  model-service:local

# Test
curl http://localhost:8081/health

# Cleanup
docker stop test
docker rm test
```

### Multi-Architecture (amd64 + arm64) for Production

**Prerequisites:**
```powershell
# Check buildx is available
docker buildx version

# Get GitHub Personal Access Token
# GitHub → Settings → Developer settings → Personal access tokens
# Create token with 'write:packages' scope
```

**Build and push (Windows):**
```powershell
# Login to GitHub Container Registry
$env:GITHUB_TOKEN = "ghp_xxxxxxxxxxxx"  # Your token
$env:GITHUB_USERNAME = "your-username"

echo $env:GITHUB_TOKEN | docker login ghcr.io -u $env:GITHUB_USERNAME --password-stdin

# Create buildx builder
docker buildx create --name multiarch --use
docker buildx inspect --bootstrap

# Build for multiple architectures
$IMAGE_NAME = "ghcr.io/doda2025-team8/model-service"
$VERSION = "v1.0.0"

docker buildx build `
  --platform linux/amd64,linux/arm64 `
  --tag ${IMAGE_NAME}:${VERSION} `
  --tag ${IMAGE_NAME}:latest `
  --push `
  .
```

**Verify:**
```powershell
docker buildx imagetools inspect ghcr.io/doda2025-team8/model-service:latest
```

## 📦 Model Files

The service requires two model files:
- `model.joblib` - Trained decision tree classifier (~100 KB)
- `preprocessor.joblib` - Complete preprocessing pipeline (~500 KB - 2 MB)

### Model Loading Strategy

1. **Check volume mount** (`/app/models/`)
2. **If not found**: Download from GitHub releases
3. **Cache models**: Persist in volume for faster restarts

**Example with persistent cache:**
```powershell
docker volume create model-cache

docker run -d -p 8081:8081 `
  -v model-cache:/app/models `
  -e GITHUB_REPO=doda2025-team8/model-service `
  --name model-service `
  ghcr.io/doda2025-team8/model-service:latest
```

## 🧪 Testing

### Quick Test (Windows)
```powershell
# Build
docker build -t model-service:test .

# Run with local models
docker run -d -p 8081:8081 `
  -v ${PWD}/output:/app/models `
  --name test-service `
  model-service:test

# Wait for startup
Start-Sleep -Seconds 10

# Test health
Invoke-RestMethod http://localhost:8081/health

# Test prediction - HAM
$body = @{ sms = "Hey, are you coming to the meeting?" } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8081/predict -Method POST -ContentType "application/json" -Body $body

# Test prediction - SPAM
$body = @{ sms = "WINNER!! Click here to claim your prize NOW!" } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8081/predict -Method POST -ContentType "application/json" -Body $body

# Check API docs
start http://localhost:8081/apidocs

# Cleanup
docker stop test-service
docker rm test-service
```

### Test Different Ports (Windows)
```powershell
# Run on port 9000
docker run -d -p 9000:9000 `
  -e MODEL_SERVICE_PORT=9000 `
  -v ${PWD}/output:/app/models `
  --name test-port `
  model-service:test

# Test
Invoke-RestMethod http://localhost:9000/health

# Cleanup
docker stop test-port
docker rm test-port
```

### Test Auto-Download (Windows)
```powershell
# Run without volume mount (will auto-download)
docker run -d -p 8081:8081 `
  -e GITHUB_REPO=doda2025-team8/model-service `
  -e MODEL_VERSION=v1.0.0 `
  --name test-download `
  model-service:test

# Watch logs (should show downloading)
docker logs -f test-download

# Wait for download to complete
Start-Sleep -Seconds 60

# Test
Invoke-RestMethod http://localhost:8081/health

# Cleanup
docker stop test-download
docker rm test-download
```