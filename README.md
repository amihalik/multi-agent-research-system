# Multi-Agent Research System

This project follows the prototype specification in `docs/prototype_spec.md`.

## Setup

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env  # and fill in secrets
```

Run the prompt watcher in one terminal:

```bash
python -m tools.lf_sync
```

Run the orchestrator in another:

```bash
python -m core.orchestrator "first question"
```
