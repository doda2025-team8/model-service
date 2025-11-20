# Model Service - SMS Spam Classifier

A containerized microservice for SMS spam detection using machine learning. Part of the REMLA course project.

## 🏗️ Architecture

- **Language**: Python 3.12.9
- **Framework**: Flask + Flasgger (Swagger UI)
- **ML Stack**: scikit-learn, NLTK
- **Container**: Docker (multi-architecture: amd64, arm64)

## 🚀 Quick Start

### Option 1: Run with Docker (Recommended)

```bash
# Pull the latest image
docker pull ghcr.io/doda2025-team8/model-service:latest

# Run with default settings (models auto-download from GitHub releases)
docker run -p 8081:8081 \
  -e GITHUB_REPO=doda2025-team8/model-service \
  ghcr.io/doda2025-team8/model-service:latest

# Run with custom port
docker run -e MODEL_SERVICE_PORT=9000 -p 9000:9000 \
  -e GITHUB_REPO=doda2025-team8/model-service \
  ghcr.io/doda2025-team8/model-service:latest

# Run with specific model version
docker run -p 8081:8081 \
  -e MODEL_VERSION=v1.0.0 \
  -e GITHUB_REPO=doda2025-team8/model-service \
  ghcr.io/doda2025-team8/model-service:latest
```

### Option 2: Run with Pre-trained Models (Volume Mount)

```bash
# Train models locally first
python src/get_data.py
python src/text_preprocessing.py
python src/text_classification.py

# Run with mounted models (no auto-download needed)
docker run -p 8081:8081 \
  -v ./output:/app/models \
  ghcr.io/doda2025-team8/model-service:latest
```

### Option 3: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('stopwords')"

# Download and train models
python get_data.py
python src/text_preprocessing.py
python src/text_classification.py

# Start the service
export MODEL_DIR=./output
python src/serve_model.py
```

## 📡 API Usage

### Health Check
```bash
curl http://localhost:8081/health
```

### Predict SMS Spam
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

### Example: Custom Configuration

```bash
docker run -p 9000:9000 \
  -e MODEL_SERVICE_PORT=9000 \
  -e MODEL_VERSION=v1.2.0 \
  -e GITHUB_REPO=doda25-team12/model-service \
  ghcr.io/doda2025-team8/model-service:latest
```

## 🏋️ Training New Models

Models are trained and released automatically using GitHub Actions:

1. Go to **Actions** tab in GitHub
2. Select **"Train and Release Model"** workflow
3. Click **"Run workflow"**
4. Enter:
   - Version: `v1.0.0` (follow semantic versioning)
   - Release notes: Description of changes
5. Workflow will:
   - Download SMS spam dataset
   - Preprocess text data
   - Train decision tree classifier
   - Create GitHub release
   - Attach model files (`model.joblib`, `preprocessor.joblib`)

## 🐳 Building the Docker Image

### Single Architecture (for testing)
```bash
docker build -t model-service:local .
docker run -p 8081:8081 model-service:local
```

### Multi-Architecture (amd64 + arm64) for Production
```bash
# Create and use buildx builder
docker buildx create --name multiarch --use

# Build and push for multiple architectures
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t ghcr.io/doda2025-team8/model-service:latest \
  --push .
```

Or use the provided script:
```bash
./build-multiarch.sh v1.0.0
```

## 📦 Model Files

The service requires two model files:
- `model.joblib` - Trained decision tree classifier
- `preprocessor.joblib` - Complete preprocessing pipeline (vectorization, TF-IDF, feature extraction)

### Model Loading Strategy

1. **Check volume mount** (`/app/models/`)
2. **If not found**: Download from GitHub releases
3. **Cache models**: Persist in volume for faster restarts

Example with persistent cache:
```bash
docker volume create model-cache
docker run -p 8081:8081 \
  -v model-cache:/app/models \
  -e GITHUB_REPO=doda2025-team8/model-service \
  ghcr.io/doda2025-team8/model-service:latest
```

## 🧪 Testing

### Run Tests
```bash
# Build the image
docker build -t model-service:test .

# Start the service
docker run -d -p 8081:8081 --name test-service \
  -v ./output:/app/models \
  model-service:test

# Run test script
./test-service.sh 8081

# Cleanup
docker stop test-service && docker rm test-service
```

### Manual Testing
```bash
# Test HAM (legitimate message)
curl -X POST http://localhost:8081/predict \
  -H "Content-Type: application/json" \
  -d '{"sms": "Hey, are you coming to the meeting tomorrow?"}'

# Test SPAM message
curl -X POST http://localhost:8081/predict \
  -H "Content-Type: application/json" \
  -d '{"sms": "WINNER!! Free entry in 2 a wkly comp to win FA Cup"}'
```
