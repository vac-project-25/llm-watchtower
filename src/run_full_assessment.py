from __future__ import annotations

from pathlib import Path
import json
import typer

from .convert_doc import convert_docx_to_txt
from .analyze_ssp_rules import load_text
from .config import Settings
from .llm_client import LLMClient


app = typer.Typer(add_completion=False, help="Milestone 6: Full assessment orchestration")


@app.command()
def main(
    input_doc: str = typer.Option(..., "--input", "-i", help="Path to SSP .docx or .pdf"),
    out_txt: str = typer.Option("artifacts/ssp_full.txt", "--out-text", help="Where to write canonical TXT"),
    instructions: str = typer.Option("rules/instructions_full.md", "--instructions"),
    ism_rules: str = typer.Option("rules/ism_full.md", "--ism"),
    out_json: str = typer.Option("artifacts/assessment_summary.json", "--out-json"),
    out_csv: str = typer.Option("artifacts/assessment_summary.csv", "--out-csv"),
    document_id: str = typer.Option("ssp_full", "--document-id"),
):
    # 1) Convert to canonical TXT
    convert_docx_to_txt(input_doc, out_txt)
    ssp = load_text(out_txt)

    # 2) Build prompt for full ruleset (kept simple for scaffold)
    instr = load_text(instructions)
    ism = load_text(ism_rules)

    schema = {
        "document_id": document_id,
        "summary": "",
        "contradictions": [],
        "rule_violations": [],
        "insufficient_evidence": [],
    }

    user = (
        "Schema:\n" + json.dumps(schema, ensure_ascii=False) +
        "\n\nINSTRUCTIONS (full):\n" + instr +
        "\n\nISM RULES (full):\n" + ism +
        "\n\nSSP TEXT:\n" + ssp +
        "\n\nReturn ONLY the JSON object."
    )

    settings = Settings.from_env()
    client = LLMClient(settings)
    out = client.chat_json(
        system=(
            "You are performing a comprehensive SSP pre-assessment. "
            "Be structured and conservative; output JSON only."
        ),
        user=user,
    )

    # 3) Write JSON
    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(out_json).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # 4) Write CSV (very simple: flatten rule_violations; others could be added later)
    try:
        import csv

        with open(out_csv, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["type", "id", "ref_or_locations", "finding_or_pair", "confidence"])
            for c in out.get("contradictions", []):
                writer.writerow([
                    "contradiction",
                    c.get("id", ""),
                    "; ".join(c.get("locations", [])),
                    f"A: {c.get('statement_a','')} | B: {c.get('statement_b','')}",
                    c.get("confidence", ""),
                ])
            for r in out.get("rule_violations", []):
                writer.writerow([
                    "rule_violation",
                    r.get("id", ""),
                    r.get("rule_ref", ""),
                    r.get("finding", ""),
                    r.get("confidence", ""),
                ])
    except Exception:
        pass

    typer.echo(f"Wrote: {out_json}\nWrote: {out_csv}")


if __name__ == "__main__":
    app()
