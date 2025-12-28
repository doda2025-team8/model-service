# Model Service - SMS Spam Classifier

A containerized microservice for SMS spam detection using machine learning.

**Team:** doda2025-team8  
**Repository:** https://github.com/doda2025-team8/model-service
**Stack:** Python 3.12 / Flask / scikit-learn / NLTK

Models download at runtime from GitHub Releases (not baked into the image), so you can update models without rebuilding.

## Running

```bash
docker pull ghcr.io/doda2025-team8/model-service:latest

docker run -d -p 8081:8081 \
  -e GITHUB_REPO=doda2025-team8/model-service \
  --name model-service \
  ghcr.io/doda2025-team8/model-service:latest
```

Wait ~30 seconds for model download, then hit `/health` to verify.

For faster startup, mount local models: `-v ./output:/app/models`

## API

**Health:** `GET /health`

**Predict:**
```bash
curl -X POST http://localhost:8081/predict \
  -H "Content-Type: application/json" \
  -d '{"sms": "WIN FREE PRIZE NOW!"}'
```

Returns:
```json
{"result": "spam", "classifier": "decision tree", "confidence": 0.92}
```

Full docs at `/apidocs`

## Config

MODEL_SERVICE_PORT: 8081 
MODEL_DIR: /app/models
MODEL_VERSION: latest
GITHUB_REPO: doda2025-team8/model-service 

## Training

Run the **Train and Release Model** workflow in [GitHub Actions](https://github.com/doda2025-team8/model-service/actions) with a version tag. Then use it with `-e MODEL_VERSION=v1.0.0`.

## Local Dev

```bash
docker build -t model-service:local .
docker run -d -p 8081:8081 -v ./output:/app/models --name test model-service:local
```

## Enviroment
Currently no environment file needed