#Dockerfile
# ============================================
# Stage 1: Builder
# ============================================
FROM python:3.12.9-slim AS builder

WORKDIR /build

# Copy requirements and install to a temporary location
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============================================
# Stage 2: Runtime
# ============================================
FROM python:3.12.9-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Download NLTK data AFTER packages are available
RUN python -c "import nltk; nltk.download('stopwords', download_dir='/usr/share/nltk_data')"

# Set NLTK data path
ENV NLTK_DATA=/usr/share/nltk_data

# Copy source files needed for serving
# We need text_preprocessing.py because serve_model.py imports from it
COPY src/serve_model.py src/serve_model.py
COPY src/model_loader.py src/model_loader.py
COPY src/text_preprocessing.py src/text_preprocessing.py

# Create models directory for volume mounts and caching
RUN mkdir -p /app/models

# Environment variables (can be overridden at runtime)
ENV MODEL_SERVICE_PORT=8081
ENV MODEL_DIR=/app/models
ENV MODEL_VERSION=latest
ENV GITHUB_REPO=doda2025-team8/model-service

# Expose the configurable port
EXPOSE ${MODEL_SERVICE_PORT}

# Health check (increased start period for model download)
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:${MODEL_SERVICE_PORT}/health', timeout=5)" || exit 1

# Run the model service
CMD ["python", "src/serve_model.py"]