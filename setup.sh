#!/bin/bash
# AnythingLLM Setup Script
# Sets up the AnythingLLM service with Ollama integration

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo " AnythingLLM Setup for RoyalTek"
echo "========================================"
echo ""

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed."
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not installed."
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker is installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "IMPORTANT: Please edit .env to configure your settings."
else
    echo "✓ .env file already exists"
fi

# Create required directories (BEFORE Docker starts)
# Pre-create all storage subdirectories that AnythingLLM needs
# This prevents Docker from creating them as root
echo "Creating required directories..."
mkdir -p storage
mkdir -p storage/documents/custom-documents
mkdir -p storage/lancedb
mkdir -p storage/vector-cache
mkdir -p storage/models/context-windows
mkdir -p storage/comkey
mkdir -p documents
mkdir -p scripts/wiki_export
echo "✓ Directories created"

# Fix ownership for container (runs as UID 1000)
# This is required because bind mounts need correct permissions
# mkdir creates directories as current user, so we must always chown
CONTAINER_UID=1000
echo "Setting storage ownership for container (UID $CONTAINER_UID)..."
if [ "$(id -u)" = "$CONTAINER_UID" ]; then
    # Already running as container UID, no chown needed
    echo "✓ Already running as UID $CONTAINER_UID"
elif [ "$(id -u)" = "0" ]; then
    # Running as root
    chown -R $CONTAINER_UID:$CONTAINER_UID storage/
    echo "✓ Storage ownership set"
elif command -v sudo &> /dev/null; then
    sudo chown -R $CONTAINER_UID:$CONTAINER_UID storage/
    echo "✓ Storage ownership set"
else
    echo "Warning: Cannot set ownership. You may need to run:"
    echo "  sudo chown -R $CONTAINER_UID:$CONTAINER_UID storage/"
fi

# Build and start containers
echo ""
echo "Building and starting AnythingLLM..."
if docker compose version &> /dev/null; then
    docker compose up -d --build
else
    docker-compose up -d --build
fi

# Wait for service to be ready
echo ""
echo "Waiting for AnythingLLM to start..."
MAX_WAIT=60
WAIT_TIME=0
while ! curl -s http://localhost:3001/api/ping > /dev/null 2>&1; do
    if [ $WAIT_TIME -ge $MAX_WAIT ]; then
        echo "Warning: AnythingLLM did not respond within $MAX_WAIT seconds."
        echo "It may still be starting. Check with: docker logs royaltek-anythingllm"
        break
    fi
    sleep 2
    WAIT_TIME=$((WAIT_TIME + 2))
    echo "  Waiting... ($WAIT_TIME seconds)"
done

if curl -s http://localhost:3001/api/ping > /dev/null 2>&1; then
    echo "✓ AnythingLLM is running!"
fi

# Post-start permission fix (in case container created new directories as root)
echo ""
echo "Verifying storage permissions..."
ROOT_OWNED=$(find storage -user root 2>/dev/null | head -1)
if [ -n "$ROOT_OWNED" ]; then
    echo "Fixing root-owned directories in storage..."
    if [ "$(id -u)" = "0" ]; then
        chown -R $CONTAINER_UID:$CONTAINER_UID storage/
    elif command -v sudo &> /dev/null; then
        sudo chown -R $CONTAINER_UID:$CONTAINER_UID storage/
    else
        echo "Warning: Some directories are owned by root. Run:"
        echo "  sudo chown -R $CONTAINER_UID:$CONTAINER_UID storage/"
    fi
fi
echo "✓ Storage permissions verified"

echo ""
echo "========================================"
echo " Setup Complete!"
echo "========================================"
echo ""
echo "Next Steps:"
echo ""
echo "1. Open AnythingLLM in your browser:"
echo "   http://localhost:3001"
echo ""
echo "2. Complete the initial setup wizard:"
echo "   - Select Ollama as LLM Provider"
echo "   - Enter Ollama URL: http://192.168.145.70:11434"
echo "   - Select model: gpt-oss:120b"
echo ""
echo "3. Generate an API key for document import:"
echo "   Settings → Developer → API Keys"
echo ""
echo "4. Run the wiki import script:"
echo "   ./import_wiki.sh"
echo ""
