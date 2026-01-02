# AnythingLLM with Ollama + MediaWiki Import

A containerized AnythingLLM setup with Ollama LLM integration and MediaWiki content import capability.

## Features

- 🤖 **AnythingLLM** - Chat with your documents using any LLM
- 🦙 **Ollama Integration** - Use local LLM models
- 📚 **MediaWiki Import** - Automatically scrape and import wiki content
- 🐳 **Docker-based** - Easy deployment and management

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/anythingllm-ollama-wiki.git
cd anythingllm-ollama-wiki

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings (Ollama URL, wiki URL, etc.)

# 3. Run setup
./setup.sh

# 4. Open AnythingLLM in browser
#    http://localhost:3001

# 5. Complete initial setup in the UI:
#    - LLM Provider: Ollama
#    - Ollama URL: (your Ollama server URL from .env)
#    - Model: (your model name)

# 6. Generate API key (Settings → Developer → API Keys)
#    Add to .env: ANYTHINGLLM_API_KEY=your-key

# 7. Import MediaWiki content (optional)
./import_wiki.sh
```

## Configuration

All settings are configured via `.env` file. Copy `.env.example` to `.env` and customize:

| Setting | Description | Example |
|---------|-------------|---------|
| `OLLAMA_BASE_PATH` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL_PREF` | LLM model name | `llama3`, `mistral`, `codellama` |
| `EMBEDDING_MODEL_PREF` | Embedding model | `nomic-embed-text` |
| `MEDIAWIKI_URL` | MediaWiki server URL | `http://wiki.example.com` |
| `ANYTHINGLLM_API_KEY` | API key for imports | Generated in UI |

## Prerequisites

- Docker & Docker Compose
- Python 3.8+ (for wiki import)
- Ollama server (local or remote)

## File Structure

```
anythingllm-ollama-wiki/
├── docker-compose.yml    # Container configuration
├── .env.example          # Configuration template
├── .env                  # Your local config (not versioned)
├── setup.sh              # Initial setup script
├── cleanup.sh            # Reset everything
├── import_wiki.sh        # MediaWiki import script
├── scripts/
│   ├── scrape_mediawiki.py      # Wiki content scraper
│   ├── upload_to_anythingllm.py # Document uploader
│   └── requirements.txt         # Python dependencies
└── storage/              # AnythingLLM data (not versioned)
```

## Usage

### Docker Operations

```bash
# Start service
docker compose up -d

# View logs
docker logs -f anythingllm

# Stop service
docker compose down

# Restart service
docker compose restart

# Reset everything (clean slate)
./cleanup.sh
```

### MediaWiki Import

```bash
# Full import (scrape + upload)
./import_wiki.sh

# Manual steps:
source scripts/venv/bin/activate
python3 scripts/scrape_mediawiki.py --url your-wiki.com
python3 scripts/upload_to_anythingllm.py --api-key YOUR_KEY
deactivate
```

## Troubleshooting

### Cannot connect to Ollama

1. If Ollama is on localhost, use `http://host.docker.internal:11434` in `.env`
2. If Ollama is on another server, ensure network connectivity
3. Test connection:
   ```bash
   curl http://your-ollama-server:11434/api/tags
   ```

### AnythingLLM not responding

```bash
docker ps -a | grep anythingllm
docker logs anythingllm
docker compose restart
```

### Permission errors on storage

The setup script automatically handles permissions. If you encounter issues:
```bash
sudo chown -R 1000:1000 storage/
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│                 │     │                  │     │                 │
│  MediaWiki      │────▶│  AnythingLLM     │────▶│  Ollama Server  │
│  (your wiki)    │     │  localhost:3001  │     │  (your server)  │
│                 │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                       │
        │    (1) Scrape         │    (2) Query
        └───────────────────────┘
```

## License

MIT

## Resources

- [AnythingLLM](https://github.com/Mintplex-Labs/anything-llm)
- [Ollama](https://github.com/ollama/ollama)
- [MediaWiki API](https://www.mediawiki.org/wiki/API:Main_page)
