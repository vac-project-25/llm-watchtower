from __future__ import annotations

import typer

from .config import Settings
from .llm_client import LLMClient


app = typer.Typer(add_completion=False, help="Milestone 1: Hello, LLM")


@app.command()
def main(
    question: str = typer.Option(
        "In one sentence, what is the goal of Project Watchtower?",
        "--question",
        "-q",
        help="Question to ask the model.",
    )
):
    """Ask a question to the configured LLM and print the answer."""
    settings = Settings.from_env()
    client = LLMClient(settings)
    system = "You are a concise assistant. Answer briefly and factually."
    answer = client.chat(system=system, user=question)
    typer.echo(answer)


if __name__ == "__main__":
    app()
