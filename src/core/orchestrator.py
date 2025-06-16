from typing import List
import asyncio

from .llm import call_llm
from .models import Query, AgentRun

async def run_subagent(prompt: str) -> str:
    return call_llm(prompt)

async def orchestrate(question: str) -> str:
    """Simple orchestrator that calls one sub-agent and returns result."""
    tasks: List[asyncio.Task] = []
    tasks.append(asyncio.create_task(run_subagent(question)))
    results = await asyncio.gather(*tasks)
    return "\n".join(results)
