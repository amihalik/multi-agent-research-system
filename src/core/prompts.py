from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"

def load(name: str) -> str:
    """Load a Jinja2 template from the prompts directory."""
    return (PROMPT_DIR / name).read_text()
