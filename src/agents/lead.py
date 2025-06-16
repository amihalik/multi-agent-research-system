from ..core.llm import call_llm


def plan(question: str) -> str:
    """Lead agent that plans research."""
    return call_llm(question)
