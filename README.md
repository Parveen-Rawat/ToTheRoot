## ToTheRoot

Autonomous AI-assisted penetration testing framework.
Built on CPTS methodology. Runs fully offline. No cloud APIs.

ToTheRoot combines network scanning, attack-surface analysis, and a local LLM reasoning layer to automate the recon-to-exploitation loop — the way a senior analyst thinks through it

## How it works

Target IP/Domain
      |
   scanner.py         Nmap scan (-sC -sV) with interactive mode
      |
  nmap_parser.py      Parses output into structured JSON
      |
    rules.py          Maps open ports and services to attack vectors
      |
 rag_suggestions.py   Queries local ChromaDB RAG (seeded with CPTS methodology)
      |
     llm.py           Ollama (Llama 3.1) generates analysis and next-step guidance
      |
    cli.py            Orchestrates the full pipeline end to end


## What's included
- `cli.py` — orchestrates the full scan and analysis pipeline.
- `scanner.py` — interactive nmap scan helper.
- `nmap_parser.py` — parses nmap text output into structured JSON.
- `rules.py` — maps common services and open ports to attack vectors.
- `rag_suggestions.py` — integrates local RAG knowledge for CPTS-style guidance.
- `query_rag.py` — ask the local knowledge base questions.
- `ingest_notes.py` — ingest personal notes into a local ChromaDB store.
- `llm.py` — local Ollama wrapper for generating analysis output.


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

## Built for
Lab environments, CTF assessments, and CPTS/OSCP preparation.
Only run against targets you have explicit authorization to test.


## Requirements
- Install dependencies with `pip install -r requirements.txt`
- Ollama must be installed separately and available via the `ollama` CLI if you use LLM features.

## License
This project is released under the MIT License. See `LICENSE` for details.

## Author
Parveen Rawat — [Portfolio](https://parveen-rawat.github.io)

---

