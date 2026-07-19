# LADS Discord Bot RAG

A Discord roleplay bot powered by a Retrieval-Augmented Generation (RAG) pipeline, built to deliver immersive, character-accurate conversations with characters from *Love and Deepspace*.

## How It Works

The bot combines three layers of context to generate in-character responses:

1. **Character lore** — scraped from wiki and fan-translation sources, chunked, and stored in a vector database for semantic retrieval.
2. **Long-term user memory** — meaningful past conversations, filtered and embedded so the character can recall relevant history with a specific user.
3. **Short-term conversation history** — the most recent exchanges with a user, kept for continuity within a session.

These are assembled into a system prompt and sent to an LLM to generate the character's response, which is then sent back to Discord.

## Architecture

```
Discord message (@mention)
        │
        ▼
  RAG Pipeline
    ├── Character lore retrieval   (ChromaDB)
    ├── Long-term memory retrieval (ChromaDB)
    ├── Recent conversation fetch  (SQLite)
    ├── LLM response generation    (Groq API)
    └── Save conversation          (ChromaDB + SQLite)
        │
        ▼
  Response sent back to Discord
```

### Components

| Component | Description |
|---|---|
| **Scraper** | Playwright-based scraper for Fandom wiki and Substack sources, with fallback CSS selectors. Run separately via CLI; excluded from the Docker image. |
| **Chunker** | Splits and cleans scraped text into overlapping word-based chunks for embedding. |
| **Vector store (ChromaDB)** | Stores character lore and long-term user memory as embeddings (`BAAI/bge-small-en-v1.5`), queried with a distance threshold of 1.4. |
| **Relational store (SQLite)** | Stores short-term conversation history per user (7-day TTL). |
| **LLM (Groq)** | Generates in-character responses using `openai/gpt-oss-120b`. |
| **Bot** | `discord.py`-based, responds via @mention, splits long replies to fit Discord's message limits. |

## Getting Started

### Prerequisites

- Python 3.11+
- A Discord bot token
- A Groq API key

### Installation

```bash
git clone https://github.com/Norumai01/LADS_Discord_Bot_RAG.git
cd LADS_Discord_Bot_RAG
pip install -r requirements.txt
playwright install chromium
```

### Configuration

Copy `.env.example` to `.env` and fill in the values:

```
DISCORD_TOKEN=
LLM_KEY=
GROQ_MODEL=
WRITE_LOGS_FILE=
```

### Scraping Character Data

```bash
# Scrape and save all configured characters
python scraper.py --all

# Or scrape/save individually
python scraper.py --scrape
python scraper.py --save
```

### Running the Bot

```bash
python main_sylus.py
```

## Docker

The bot (excluding the scraper) is containerized for deployment.

```bash
docker compose up -d --build
```

- Built on `python:3.11-slim`, ARM64-compatible
- Embedding model and NLTK corpus baked in at build time (no internet required at runtime)
- Resource limits: 2 CPUs / 4GB RAM (configurable in `docker-compose.yml`)

## Roadmap

- [ ] Migrate deployment from Docker to rootless Podman with user-level systemd/quadlet services
- [ ] Expand character support beyond Sylus (Caleb, Xavier)
- [ ] Add sentient enhancements to the bot (e.g., respond to random conversation)

## Copyright

© 2026 Norumai. All rights reserved.

This applies to the original source code of this project (the bot, RAG pipeline, and related tooling). It does not extend to *Love and Deepspace*, its characters, or any scraped wiki/fan-translation content, which remain the property of their respective owners.

## Disclaimer

This is a fan-made, non-commercial project built for a small friend group. All characters and source material belong to their respective owners (Papergames / *Love and Deepspace*).