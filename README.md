# AnythingLLM Service for RoyalTek

A containerized AnythingLLM setup with Ollama integration and MediaWiki content import.

## Quick Start

```bash
# 1. Run setup
./setup.sh

# 2. Open AnythingLLM
#    http://localhost:3001

# 3. Complete initial setup in the UI:
#    - LLM Provider: Ollama
#    - Ollama URL: http://192.168.145.70:11434
#    - Model: gpt-oss:120b

# 4. Generate API key (Settings → Developer → API Keys)
#    Add to .env: ANYTHINGLLM_API_KEY=your-key

# 5. Import MediaWiki content
./import_wiki.sh
```

## Configuration

| Setting | Value |
|---------|-------|
| Ollama Server | `192.168.145.70:11434` |
| Ollama Model | `gpt-oss:120b` |
| MediaWiki URL | `http://wiki.royaltek.com` |
| AnythingLLM Port | `3001` |

Edit `.env` to customize settings.

## Prerequisites

- Docker & Docker Compose
- Python 3.8+ (for wiki import)
- Network access to:
  - Ollama server at `192.168.145.70`
  - MediaWiki at `wiki.royaltek.com`

## File Structure

```
royaltekanythingllm/
├── docker-compose.yml    # Container configuration
├── .env.example          # Configuration template
├── setup.sh              # Initial setup script
├── import_wiki.sh        # MediaWiki import script
├── scripts/
│   ├── scrape_mediawiki.py      # Wiki content scraper
│   ├── upload_to_anythingllm.py # Document uploader
│   └── requirements.txt         # Python dependencies
├── storage/              # AnythingLLM data (persistent)
└── documents/            # Uploaded documents
```

## Manual Commands

### Docker Operations

```bash
# Start service
docker compose up -d

# View logs
docker logs -f royaltek-anythingllm

# Stop service
docker compose down

# Restart service
docker compose restart
```

### MediaWiki Import

```bash
# Activate Python environment
source scripts/venv/bin/activate

# Scrape wiki (saves to scripts/wiki_export/)
python3 scripts/scrape_mediawiki.py --url wiki.royaltek.com

# Upload to AnythingLLM
python3 scripts/upload_to_anythingllm.py --api-key YOUR_KEY

# Deactivate environment
deactivate
```

## Troubleshooting

### Cannot connect to Ollama

1. Verify Ollama server is running:
   ```bash
   curl http://192.168.145.70:11434/api/tags
   ```

2. Check if model exists:
   ```bash
   curl http://192.168.145.70:11434/api/show -d '{"name":"gpt-oss:120b"}'
   ```

### AnythingLLM not responding

```bash
# Check container status
docker ps -a | grep anythingllm

# View logs
docker logs royaltek-anythingllm

# Restart container
docker compose restart
```

### MediaWiki connection issues

```bash
# Test wiki connectivity
curl -I http://wiki.royaltek.com

# Test with Python
python3 -c "import mwclient; site = mwclient.Site('wiki.royaltek.com', path='/'); print('OK')"
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│                 │     │                  │     │                 │
│  MediaWiki      │────▶│  AnythingLLM     │────▶│  Ollama Server  │
│  wiki.royaltek  │     │  localhost:3001  │     │  192.168.145.70 │
│                 │     │                  │     │  gpt-oss:120b   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                       │
        │    (1) Scrape         │    (2) Query
        └───────────────────────┴──────────────────────────────────▶
```

## Support

For issues with:
- **AnythingLLM**: https://github.com/Mintplex-Labs/anything-llm
- **Ollama**: https://github.com/ollama/ollama
- **MediaWiki API**: https://www.mediawiki.org/wiki/API:Main_page
