#!/bin/bash
# Build script for MansionNET Radio Bot Docker image

set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
IMAGE_NAME="mansion-radio-bot"
IMAGE_TAG="latest"
FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"

echo "╔════════════════════════════════════════════╗"
echo "║  Building $IMAGE_NAME Docker Image        ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "❌ Docker daemon is not running"
    exit 1
fi

echo "[1/4] Checking project structure..."
if [ ! -f "$PROJECT_DIR/Dockerfile" ]; then
    echo "❌ Dockerfile not found in $PROJECT_DIR"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
    echo "❌ requirements.txt not found in $PROJECT_DIR"
    exit 1
fi

echo "✓ Project structure valid"
echo ""

echo "[2/4] Building Docker image: $FULL_IMAGE"
docker build \
    -t "$FULL_IMAGE" \
    -f "$PROJECT_DIR/Dockerfile" \
    "$PROJECT_DIR"

echo ""
echo "[3/4] Verifying image..."
if docker image inspect "$FULL_IMAGE" > /dev/null 2>&1; then
    echo "✓ Image built successfully"
    docker image inspect "$FULL_IMAGE" | grep -A1 '"Architecture"'
else
    echo "❌ Image build failed"
    exit 1
fi

echo ""
echo "[4/4] Image ready for deployment"
echo ""

echo "╔════════════════════════════════════════════╗"
echo "║  Build Complete!                          ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Image: $FULL_IMAGE"
echo ""
echo "Next steps:"
echo "  1. Use this docker-compose.yml in Portainer:"
echo "     image: $FULL_IMAGE"
echo "  2. Deploy the stack in Portainer"
echo "  3. No build step needed - just run!"
echo ""
echo "To test locally:"
echo "  docker run -e IRC_SERVER=irc.inthemansion.com $FULL_IMAGE"
echo ""
