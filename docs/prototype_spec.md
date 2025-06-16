
# Prototype Multi‑Agent Research System (local, fast‑iteration)

## 1  Scope

* Single‑machine proof‑of‑concept that  
  * takes a research question (CLI or REST)  
  * spawns up to **N parallel sub‑agents** with `asyncio.gather`  
  * returns a Markdown report + JSON trace  
  * records every run in **Langfuse** and **SQLite**  
  * lets you iterate on prompts in seconds and promote “good” versions back to Git

## 2  Tech Stack

| Concern | Tool | Notes |
|---------|------|-------|
| Package / env mgmt | **uv** | `uv venv .venv && uv pip install -r requirements.txt` |
| LLM SDK | **pydantic‑ai** | swap Anthropic / OpenAI / Groq by env var |
| Templates | **Jinja2** | `prompts/<agent>/<template>.j2` |
| Orchestration | plain Python 3.11 + `asyncio` | no Ray |
| Data models | Pydantic v2 (bundled in pydantic‑ai) |
| Persistence | SQLite via **sqlmodel** |
| Tracing / Obs | **Langfuse** (`langfuse-python`) |
| CLI | `typer` |
| Logging | `structlog` + `rich` |
| Test / Eval | **PyTest** + YAML fixtures + LLM‑as‑judge helper |

### 2.1 `requirements.txt`

```text
pydantic-ai>=0.3
langfuse-python>=2.0
jinja2>=3.1
sqlmodel>=0.0.16
aiosqlite>=0.19
typer>=0.9
structlog>=24.1
rich>=13.7
pytest>=8.2
watchdog>=4.0           # for prompt sync

Install:

uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt

3  Folder Layout

repo/
  src/
    agents/
      lead.py
      sub.py
      citation.py
    tools/
      web_search.py
    core/
      orchestrator.py
      models.py
      prompts.py
      llm.py            # pydantic‑ai + Langfuse wrapper
  prompts/
    lead/plan.j2
    sub/search.j2
    sub/reflect.j2
    citation/cite.j2
  tests/
    fixtures/*.yaml
    test_eval.py
  tools/
    lf_sync.py          # prompt watcher (see §5)
  docs/prototype_spec.md
  .env.example

4  Minimal Data‑Model (sqlmodel)

from datetime import datetime
from sqlmodel import SQLModel, Field, JSON

class Query(SQLModel, table=True):
    id: str = Field(primary_key=True)
    prompt: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AgentRun(SQLModel, table=True):
    id: str = Field(primary_key=True)
    query_id: str
    role: str                # "lead" / "sub" / "citation"
    status: str              # pending / running / done / error
    tokens: int | None = None
    result: JSON | None = None

5  Prompt Hot‑Reload Loop with Langfuse

5.1 Instrument all LLM calls once

# src/core/llm.py
from langfuse import observe
from pydantic_ai import ChatCompletion

@observe(model="anthropic/claude-3-opus")          # decorator auto‑logs to Langfuse
def call_llm(prompt: str, **params):
    return ChatCompletion.create(prompt=prompt, **params).content

5.2 Push local prompt files to Langfuse on every save

# tools/lf_sync.py
from pathlib import Path
from langfuse import Langfuse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

lf = Langfuse()   # uses LANGFUSE_* env vars

class Push(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith((".j2", ".baml")):
            return
        file = Path(event.src_path)
        lf.upsert_prompt(
            name=file.stem,
            text=file.read_text(),
            label="sandbox"    # never marked “production”
        )
        print("▲  pushed", file)

observer = Observer()
observer.schedule(Push(), "prompts/", recursive=True)
observer.start()
observer.join()

Run once in a separate terminal:

python -m tools.lf_sync

Now:
	1.	Edit *.j2 → auto‑pushed to Langfuse as “sandbox” version.
	2.	Try variants in Langfuse Playground.
	3.	When satisfied, pull the latest text and overwrite your file:

from pathlib import Path
from langfuse import Langfuse
lf = Langfuse()
p = lf.get_prompt("lead_plan", label="sandbox")
Path("prompts/lead/plan.j2").write_text(p.prompt)

Commit to Git—your repo remains the single source of truth.

6  Execution Flow

sequenceDiagram
    autonumber
    user→>CLI: research question
    CLI→>LeadAgent: plan()
    LeadAgent->>+SubAgent[N]: async run()
    SubAgent-->>LeadAgent: findings
    LeadAgent->>CitationAgent: add_citations()
    CitationAgent-->>LeadAgent: final.md
    LeadAgent->>SQLite: persist trace
    LeadAgent->>Langfuse: send trace
    LeadAgent-->>user: markdown + JSON trace

7  Testing & Edge‑Case Capture
	1.	YAML fixtures live in tests/fixtures/*.yaml.
	2.	pytest loads each fixture, runs orchestrator, and calls an LLM‑judge (also via call_llm) to score.
	3.	Any manual failure you spot in Langfuse ➜ “Add to dataset: edge‑cases”; CI pulls that dataset and adds it to the test matrix.

Example fixture:

- id: fusion_investors
  prompt: "Who funds fusion energy startups?"
  expect:
    rubric: "factuality+citations+completeness"
    min_score: 0.8

8  Daily Dev Loop

edit prompt.j2
   ↓ auto‑push
Langfuse Playground
   ↓ tweak / run / save
local CLI or pytest run
   ↓ trace visible in Langfuse
edge‑case? add to dataset
   ↓
happy? pull prompt text → git commit

9  Setup Checklist
	•	uv venv .venv && source .venv/bin/activate
	•	uv pip install -r requirements.txt
	•	Copy .env.example → .env and fill LANGFUSE_*, provider API keys.
	•	Run python -m tools.lf_sync in one terminal.
	•	Run python -m core.orchestrator "first query" in another.
	•	Add at least five YAML tests; run pytest -q.