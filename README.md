# 🏢 Local Multi-Agent Workspace & Executive Hub

An offline, privacy-first multi-agent development environment engineered specifically for local execution on Apple Silicon (M-Series Core Architecture). This workspace uses **Playwright** to scrape complex, Javascript-rendered job listings, utilizes a local **SQLite** database to intelligently cache listings, and leverages **Ollama** to orchestrate intelligence workflows—ensuring no data or resumes ever leave your local Mac.

---

## 🕹️ Architecture & Features

- **Local Processing Core**: Complete data isolation. Your data is processed entirely on local hardware via Ollama.
- **Smart Web Scraping Cache**: Embedded SQLite database hashes unique target job URLs. It skips headless browser delays by serving cached data instantly, and auto-refreshes data if it passes a user-defined age threshold (configured via UI slider).
- **Asynchronous JS Layout Rendering**: Bypasses strict anti-scraping blocks and dynamic React/Vue hydration using a direct background Playwright execution loop.
- **Multi-Agent Specialist Guild**:
  - **Cover Letter Agent**: Crafts high-impact corporate introductory letters optimized for local contextual compliance.
  - **Resume Tailor Agent**: Compiles targeted adjustments to map your background directly onto core job keywords.
  - **Interview Coach**: Processes job descriptions and resumes to generate a comprehensive local interview preparation module.
- **Typography Compilation**: Directly compiles edited markdown from your canvas window into a printable document PDF file locally.

---

## 🏗️ Project Layout

```text
├── main.py                 # Automated orchestration entry point (starts/kills servers)
├── your_streamlit_script.py # Streamlit interface and core UI logic
├── job_cache.db            # Local file-based SQLite cache (Auto-generated)
├── requirements.txt        # Optional Python packages lockfile
├── pyproject.toml          # uv project configuration and constraint rules
└── src/
    ├── __init__.py
    ├── agents.py           # AgentOrchestrator and PDF compilation engines
    └── cache.py            # SQLite cache tables and timestamp validation logic
```

---

## 🚀 Quick Start (Local Setup)

### 1. Prerequisites
Ensure you have the native **Ollama** engine installed on your Mac. You do not need to run it yourself; the project runner file handles lifecycle triggers automatically.

If you don't have it, install it via Homebrew:
```bash
brew install --cask ollama
```

Pull the model matching your script configuration (e.g., `llama3` or `llama3.2`):
```bash
ollama pull llama3
```

### 2. Environment Installation
This project leverages `uv` for high-speed, predictable dependency resolution. Initialize your setup and install the required headless browser frameworks:

```bash
# Install required packages through uv pip environment wrapper
uv pip install streamlit langchain-ollama playwright beautifulsoup4 html2text httpx pandas

# Install necessary Playwright headless browser binaries
uv run playwright install chromium
```

### 3. Run the Unified Workspace
Run the automated orchestration script. This script boots the background Ollama server, validates network health, and launches your Streamlit dashboard.

```bash
uv run python main.py
```

*Note: When you shut down your Streamlit workspace using `Ctrl+C` or the UI shutdown button, the script will automatically terminate all local LLM background servers (`ollama`, `llama-server`) to reclaim your Mac's RAM footprint.*

---

## 📊 Local Resource Auditing

The system embeds a hardware telemetry panel directly below the output canvas. This tool captures:
- Inbound Input / Prompt token density.
- Outbound token synthesis velocity.
- Cost accounting overhead (Hardcoded to `$0.00` to show the efficiency of local Apple Metal acceleration).
