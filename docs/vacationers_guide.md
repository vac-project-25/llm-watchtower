# Watchtower Vacationers Guide

This guide explains what you’ll build, how to work through the milestones, and what “done” looks like for the internship prototype.

## What you’re building

An API‑first pipeline that ingests SSP documents (DOCX/PDF), converts them to text, and uses an LLM to:
- Spot contradictions and missing evidence early
- Check alignment to a small set of instructions + ISM rules
- Produce a structured JSON (and CSV) summary for triage

Start with deterministic CLI scripts, then wrap in a minimal UI for demo.

## Milestones (with acceptance checks)

1) Hello, LLM (API)
- Script calls gpt‑4o‑mini (config via env vars) and prints an answer
- Files: `src/hello_llm.py`, `docs/api_llm_setup.md`

2) Text analytics on a TXT (deterministic)
- Counts, duplicates, single‑word count; emits JSON
- Files: `data/animals.txt`, `src/analyze_text.py`

3) Reliable DOCX→TXT (Pandoc)
- Convert `.docx` to text; counts match the TXT baseline via a test
- Files: `src/convert_doc.py`, `tests/test_animals_equivalence.py`

4) Contradiction detection (first 3 SSP pages)
- Seed obvious contradictions; model returns structured JSON per contract
- File: `src/find_contradictions.py`

5) Rules‑aware analysis (subset)
- Use small sample instructions + ISM subset; output separates contradictions, rule‑violations, insufficient‑evidence
- Files: `rules/instructions_sample.md`, `rules/ism_sample.md`, `src/analyze_ssp_rules.py`

6) Full SSP + full rules
- Scales to full doc + full rules; completes in reasonable time (<~5 min target); writes JSON + CSV
- Files: `src/run_full_assessment.py`, `artifacts/assessment_summary.json`, `.csv`

7) Wrap in a simple app (optional in week 4)
- File upload → results view; export JSON/CSV; choose Gradio or Streamlit

8) Demo
- One happy path + one edge case (missing evidence). Add a short demo script to README and optionally a GIF.

## Output contract (Milestones 4–6)

Return one JSON object:

```json
{
  "document_id": "string",
  "summary": "one-paragraph high-level findings",
  "contradictions": [
    {"id": "c1", "statement_a": "text", "statement_b": "text", "locations": ["p2: s1"], "confidence": 0.0}
  ],
  "rule_violations": [
    {"id": "r1", "rule_ref": "ISM-XX.123", "finding": "text", "evidence": "snippet", "confidence": 0.0}
  ],
  "insufficient_evidence": [
    {"control": "control-id-or-rule", "reason": "what is missing"}
  ]
}
```

Keep temperature low (0.0–0.2), prefer small prompts, and return JSON only.

## How to run (PowerShell)

Make sure you’ve completed setup in `docs/api_llm_setup.md`.

- Hello LLM
```powershell
python -m src.hello_llm --question "In one sentence, what is this prototype for?"
```

- Deterministic analytics
```powershell
python -m src.analyze_text --file data/animals.txt --question counts
python -m src.analyze_text --file data/animals.txt --question duplicates
python -m src.analyze_text --file data/animals.txt --question "count:giraffe"
```

- DOCX → TXT (requires Pandoc)
```powershell
python -m src.convert_doc --input data/animals.docx --output artifacts/animals.txt
```

- Contradictions on SSP excerpt
```powershell
python -m src.find_contradictions --file artifacts/ssp_excerpt.txt --document-id ssp_sample_p3
```

- Rules‑aware analysis (subset)
```powershell
python -m src.analyze_ssp_rules --ssp artifacts/ssp_excerpt.txt --instructions rules/instructions_sample.md --ism rules/ism_sample.md --document-id ssp_sample
```

- Full assessment (JSON + CSV)
```powershell
python -m src.run_full_assessment --input data/ssp_full.docx --out-text artifacts/ssp_full.txt --instructions rules/instructions_full.md --ism rules/ism_full.md --out-json artifacts/assessment_summary.json --out-csv artifacts/assessment_summary.csv --document-id ssp_full
```

## Repository layout

```
src/                      # CLI scripts and helpers
  analyze_text.py
  analyze_ssp_rules.py
  convert_doc.py
  find_contradictions.py
  hello_llm.py
  llm_client.py
  config.py
  run_full_assessment.py
rules/                    # Sample rules (subset now; full later)
  instructions_sample.md
  ism_sample.md
data/
  animals.txt            # Sample input for deterministic analytics
artifacts/                # Generated TXT/JSON/CSV (kept out of git)
  .gitkeep
tests/
  test_animals_equivalence.py
docs/
  api_llm_setup.md
  vacationers_guide.md
```

## Guardrails

- Privacy: use synthetic/redacted SSP content for the API; don’t upload sensitive info.
- Determinism: low temperature, explicit schema, small prompts; add simple tests where possible.
- Cost/latency: chunk long docs, cap tokens, cache responses when iterating.
- Pluggable provider: code is written to work with OpenAI‑compatible HTTP; swap later if needed.

## What the end product looks like

- A repeatable CLI pipeline that converts SSPs to text, runs contradiction and rules checks, and produces structured outputs (JSON + CSV).
- A minimal UI (if chosen) that accepts file uploads and shows a human‑readable summary with downloadable artifacts.
- A short demo showing one happy path and one edge case.
