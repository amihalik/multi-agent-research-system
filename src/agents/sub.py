from ..core.llm import call_llm


def search(query: str) -> str:
    """Sub agent that performs a search."""
    return call_llm(query)
