from __future__ import annotations

import json
from pathlib import Path
import typer

from .config import Settings
from .llm_client import LLMClient


SYSTEM = (
    "You are assessing an SSP against provided instructions and ISM rules. "
    "Output a single JSON object with sections: contradictions, rule_violations, insufficient_evidence. "
    "Include brief evidence snippets and conservative confidence scores."
)


def load_text(path: str) -> str:
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else ""


app = typer.Typer(add_completion=False, help="Milestone 5: Rules-aware SSP analysis (subset)")


@app.command()
def main(
    ssp_txt: str = typer.Option(..., "--ssp", help="Path to SSP text (converted)"),
    instructions: str = typer.Option("rules/instructions_sample.md", "--instructions"),
    ism_rules: str = typer.Option("rules/ism_sample.md", "--ism"),
    document_id: str = typer.Option("ssp_sample", "--document-id"),
):
    ssp = load_text(ssp_txt)
    instr = load_text(instructions)
    ism = load_text(ism_rules)

    schema = {
        "document_id": document_id,
        "summary": "",
        "contradictions": [],
        "rule_violations": [
            {
                "id": "r1",
                "rule_ref": "ISM-XX.123",
                "finding": "text",
                "evidence": "snippet",
                "confidence": 0.0,
            }
        ],
        "insufficient_evidence": [
            {"control": "control-or-rule-id", "reason": "what is missing"}
        ],
    }

    user = (
        "Schema:\n" + json.dumps(schema, ensure_ascii=False) +
        "\n\nINSTRUCTIONS (subset):\n" + instr +
        "\n\nISM RULES (subset):\n" + ism +
        "\n\nSSP TEXT:\n" + ssp +
        "\n\nReturn ONLY the JSON object."
    )

    settings = Settings.from_env()
    client = LLMClient(settings)
    out = client.chat_json(system=SYSTEM, user=user)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
