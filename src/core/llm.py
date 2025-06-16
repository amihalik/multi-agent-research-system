from langfuse import observe
from pydantic_ai import ChatCompletion

@observe(model="anthropic/claude-3-opus")
def call_llm(prompt: str, **params):
    """Wrapper around ChatCompletion.create that also logs to Langfuse."""
    return ChatCompletion.create(prompt=prompt, **params).content
