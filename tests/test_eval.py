import yaml
from pathlib import Path

from src.core.orchestrator import orchestrate

FIXTURES = Path(__file__).parent / "fixtures"

def load_cases():
    for file in FIXTURES.glob("*.yaml"):
        with file.open() as f:
            yield yaml.safe_load(f)


def test_cases():
    for case in load_cases():
        result = orchestrate(case["prompt"])  # would normally be async
        assert result is not None
