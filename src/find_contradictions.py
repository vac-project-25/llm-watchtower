from __future__ import annotations

import json
from pathlib import Path
import typer

from .config import Settings
from .llm_client import LLMClient


CONTRACT = {
    "document_id": "string",
    "summary": "string",
    "contradictions": [
        {
            "id": "c1",
            "statement_a": "text",
            "statement_b": "text",
            "locations": ["p2: s1"],
            "confidence": 0.0,
        }
    ],
    "rule_violations": [],
    "insufficient_evidence": [],
}


SYSTEM = (
    "You are verifying contradictions in a Security System Plan (SSP). "
    "Only return a single JSON object matching the provided schema. "
    "If evidence is unclear, place items under 'insufficient_evidence'. "
    "Be conservative; prefer fewer, higher-confidence findings."
)


app = typer.Typer(add_completion=False, help="Milestone 4: Contradiction detection (first 3 pages)")


@app.command()
def main(
    file: str = typer.Option(..., "--file", "-f", help="Path to input .txt SSP excerpt"),
    document_id: str = typer.Option("ssp_sample_p3", "--document-id", help="Identifier for the document"),
):
    text = Path(file).read_text(encoding="utf-8")
    settings = Settings.from_env()
    client = LLMClient(settings)
    user = (
        "Schema:\n" + json.dumps(CONTRACT, ensure_ascii=False) +
        "\n\nDocument ID: " + document_id +
        "\n\nSSP Text (first 3 pages or excerpt):\n" + text +
        "\n\nReturn ONLY the JSON object."
    )
    out = client.chat_json(system=SYSTEM, user=user)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
