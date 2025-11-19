#!/bin/bash
# Multi-architecture Docker build script
# Builds for amd64 and arm64 architectures

set -e  # Exit on error

# Configuration
IMAGE_NAME="ghcr.io/doda2025-team8/model-service"  # Update with your org
VERSION="${1:-latest}"  # Use first argument or 'latest'
BUILDER_NAME="multiarch-builder"

echo "================================================"
echo "Building Multi-Architecture Docker Image"
echo "================================================"
echo "Image: ${IMAGE_NAME}:${VERSION}"
echo "Architectures: linux/amd64, linux/arm64"
echo "================================================"

# Check if docker buildx is available
if ! docker buildx version > /dev/null 2>&1; then
    echo "Error: docker buildx is not available"
    echo "Please install Docker Buildx: https://docs.docker.com/buildx/working-with-buildx/"
    exit 1
fi

# Create or use existing builder
if docker buildx inspect ${BUILDER_NAME} > /dev/null 2>&1; then
    echo "Using existing builder: ${BUILDER_NAME}"
    docker buildx use ${BUILDER_NAME}
else
    echo "Creating new builder: ${BUILDER_NAME}"
    docker buildx create --name ${BUILDER_NAME} --use
fi

# Bootstrap the builder
echo "Bootstrapping builder..."
docker buildx inspect --bootstrap

# Build and push for multiple architectures
echo ""
echo "Building image for multiple architectures..."
docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag ${IMAGE_NAME}:${VERSION} \
    --tag ${IMAGE_NAME}:latest \
    --push \
    .

echo ""
echo "================================================"
echo "✓ Build completed successfully!"
echo "================================================"
echo "Images pushed:"
echo "  - ${IMAGE_NAME}:${VERSION}"
echo "  - ${IMAGE_NAME}:latest"
echo ""
echo "Pull with:"
echo "  docker pull ${IMAGE_NAME}:${VERSION}"
echo "================================================"

# Optional: Create a local copy for testing
# Uncomment if you want a local copy (only for current architecture)
# echo ""
# echo "Creating local copy for testing..."
# docker buildx build \
#     --platform linux/amd64 \
#     --tag ${IMAGE_NAME}:${VERSION}-local \
#     --load \
#     .