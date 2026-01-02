#!/bin/bash
# MediaWiki Import Script
# Scrapes MediaWiki content and uploads to AnythingLLM

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo " MediaWiki Import for AnythingLLM"
echo "========================================"
echo ""

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Warning: .env file not found. Using defaults."
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3.8 or later."
    exit 1
fi
echo "✓ Python 3 is installed"

# Setup Python virtual environment
VENV_DIR="scripts/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r scripts/requirements.txt
echo "✓ Dependencies installed"

# Create export directory
EXPORT_DIR="scripts/wiki_export"
mkdir -p "$EXPORT_DIR"

# Run MediaWiki scraper
echo ""
echo "========================================"
echo " Step 1: Scraping MediaWiki"
echo "========================================"
echo ""
if [ -z "$MEDIAWIKI_URL" ]; then
    echo "Error: MEDIAWIKI_URL is not set in .env"
    echo "Please set MEDIAWIKI_URL to your wiki server URL."
    exit 1
fi

echo "Wiki URL: $MEDIAWIKI_URL"
echo "Output: $EXPORT_DIR"
echo ""

python3 scripts/scrape_mediawiki.py \
    --url "$MEDIAWIKI_URL" \
    --path "${MEDIAWIKI_PATH:-/}" \
    --output "$EXPORT_DIR" \
    ${MEDIAWIKI_USERNAME:+--username "$MEDIAWIKI_USERNAME"} \
    ${MEDIAWIKI_PASSWORD:+--password "$MEDIAWIKI_PASSWORD"}

# Check if AnythingLLM API key is configured
if [ -z "$ANYTHINGLLM_API_KEY" ]; then
    echo ""
    echo "========================================"
    echo " API Key Required"
    echo "========================================"
    echo ""
    echo "To upload documents to AnythingLLM, you need an API key."
    echo ""
    echo "1. Open AnythingLLM: http://localhost:3001"
    echo "2. Go to Settings → Developer → API Keys"
    echo "3. Create a new API key"
    echo "4. Add to .env file: ANYTHINGLLM_API_KEY=your-key-here"
    echo "5. Run this script again"
    echo ""
    echo "Alternatively, run manually:"
    echo "  python3 scripts/upload_to_anythingllm.py --api-key YOUR_KEY"
    echo ""
    deactivate
    exit 0
fi

# Upload to AnythingLLM
echo ""
echo "========================================"
echo " Step 2: Uploading to AnythingLLM"
echo "========================================"
echo ""

python3 scripts/upload_to_anythingllm.py \
    --url "${ANYTHINGLLM_URL:-http://localhost:3001}" \
    --api-key "$ANYTHINGLLM_API_KEY" \
    --documents "$EXPORT_DIR" \
    --workspace "RoyalTek Wiki"

deactivate

echo ""
echo "========================================"
echo " Import Complete!"
echo "========================================"
echo ""
echo "Your MediaWiki content has been imported to AnythingLLM."
echo "Open http://localhost:3001 and select the 'RoyalTek Wiki' workspace."
echo ""
