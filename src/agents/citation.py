from ..core.llm import call_llm


def cite(text: str) -> str:
    """Agent that adds citations."""
    return call_llm(text)
