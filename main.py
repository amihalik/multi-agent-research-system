import asyncio
import typer

from src.core.orchestrator import orchestrate

app = typer.Typer()

@app.command()
def run(question: str):
    """Run the orchestrator with the given question."""
    result = asyncio.run(orchestrate(question))
    typer.echo(result)

if __name__ == "__main__":
    app()
