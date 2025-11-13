from __future__ import annotations

import json
import re
from collections import Counter
from typing import Dict, List, Tuple

import typer


WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)


def tokenize(text: str) -> List[str]:
    return [w.lower() for w in WORD_RE.findall(text)]


def compute_word_counts(text: str) -> Dict[str, int]:
    return Counter(tokenize(text))


def duplicates(counts: Dict[str, int]) -> List[Tuple[str, int]]:
    return sorted([(w, c) for w, c in counts.items() if c > 1], key=lambda x: (-x[1], x[0]))


app = typer.Typer(add_completion=False, help="Milestone 2: Deterministic text analytics")


@app.command()
def main(
    file: str = typer.Option(..., "--file", "-f", help="Path to input text file"),
    question: str = typer.Option(
        "counts",
        "--question",
        "-q",
        help="Question type: 'counts' | 'duplicates' | 'count:<word>'",
    ),
):
    with open(file, "r", encoding="utf-8") as fh:
        text = fh.read()
    counts = compute_word_counts(text)
    payload = {
        "total_words": sum(counts.values()),
        "unique_words": len(counts),
    }

    if question == "counts":
        payload["counts"] = dict(sorted(counts.items(), key=lambda x: (-x[1], x[0])))
    elif question == "duplicates":
        payload["duplicates"] = [
            {"word": w, "count": c} for w, c in duplicates(counts)
        ]
    elif question.startswith("count:"):
        target = question.split(":", 1)[1].strip().lower()
        payload["count"] = {target: counts.get(target, 0)}
    else:
        payload["note"] = "Unknown question; returning summary only."

    typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
