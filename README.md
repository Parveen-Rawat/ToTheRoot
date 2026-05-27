## ToTheRoot

ToTheRoot is a local penetration testing framework designed for lab and CTF-style assessments. It combines network scanning, attack-surface analysis, a lightweight rule engine, and optional local LLM support for richer reporting.

## What's included
- `cli.py` — orchestrates the full scan and analysis pipeline.
- `scanner.py` — interactive nmap scan helper.
- `nmap_parser.py` — parses nmap text output into structured JSON.
- `rules.py` — maps common services and open ports to attack vectors.
- `rag_suggestions.py` — integrates local RAG knowledge for CPTS-style guidance.
- `query_rag.py` — ask the local knowledge base questions.
- `ingest_notes.py` — ingest personal notes into a local ChromaDB store.
- `llm.py` — local Ollama wrapper for generating analysis output.

## Safe public upload
This repository is configured to keep sensitive or lab-specific files out of the public repo.
- `cap_agent.py` is intentionally excluded and should not be pushed.
- `scans/`, `__pycache__/`, `*.env`, and local database files are ignored.
- No real cloud API keys or private SSH credentials are included.

## Quick start
1. Create a Python virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the CLI on an authorized lab target:

```powershell
python cli.py --target <target-ip-or-domain>
```

## Notes
- This project is intended for authorized and educational use only.
- Do not scan targets without permission.
- `cap_agent.py` and any generated reports should remain local and should not be uploaded to the public repo.

## Requirements
- Install dependencies with `pip install -r requirements.txt`
- Ollama must be installed separately and available via the `ollama` CLI if you use LLM features.

## License
This project is released under the MIT License. See `LICENSE` for details.

## Author
Parveen Rawat — https://github.com/Parveen-Rawat

---

If you prefer merging both README versions, tell me and I will craft a combined header and project summary.
