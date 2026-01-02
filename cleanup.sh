#!/bin/bash
# Cleanup Script - Remove all containers, volumes, images, and working folders
# Use this to restart the project from scratch

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo " AnythingLLM Cleanup"
echo "========================================"
echo ""
echo "This will remove:"
echo "  - Docker containers created by this project"
echo "  - Docker volumes created by this project"  
echo "  - Docker images pulled for this project"
echo "  - Working folders (storage/, documents/, scripts/wiki_export/, scripts/venv/, .venv/)"
echo ""
read -p "Are you sure? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Stopping and removing containers..."
if docker compose version &> /dev/null; then
    docker compose down -v --remove-orphans 2>/dev/null || true
else
    docker-compose down -v --remove-orphans 2>/dev/null || true
fi

# Remove specific container if still exists
docker rm -f anythingllm 2>/dev/null || true

echo "Removing Docker images..."
docker rmi mintplexlabs/anythingllm:latest 2>/dev/null || true

echo "Removing working folders..."
sudo rm -rf storage/ 2>/dev/null || rm -rf storage/ 2>/dev/null || true
rm -rf documents/
rm -rf scripts/wiki_export/
rm -rf scripts/venv/
rm -rf .venv/

echo ""
echo "========================================"
echo " Cleanup Complete!"
echo "========================================"
echo ""
echo "To start fresh, run:"
echo "  ./setup.sh"
echo ""
