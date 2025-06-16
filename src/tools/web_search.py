from ..core.llm import call_llm


def web_search(query: str) -> str:
    """Placeholder web search tool."""
    return call_llm(query)
