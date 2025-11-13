# Watchtower Use Case: AI-assisted Security Assessment Pre‑Assessment (SSP Readiness)

This document turns the business-provided slides into a concrete intern brief for Project Watchtower. The goal is to build a small but convincing prototype that helps reduce manual effort in the earliest stage of security assessment by automatically reviewing documentation for basic maturity, contradictions, and alignment to rules.

- Slide references: `images/use_case_slide_1.png`, `images/use_case_slide_2.png`.
- Audience: Project Watchtower interns (AI & Data Vacationers).
- Operating principle: API-first, privacy-preserving experimentation using a hosted LLM API (initially OpenAI gpt‑4o‑mini). No local model runtime is required.

> Important program note
>
> The business security assessment use case ultimately envisions a local/private LLM deployment for confidentiality. However, for Project Watchdown’s 4‑week internship window we will omit local hosting from scope and use a managed API (OpenAI gpt‑4o‑mini) to maximise velocity. The code should keep the provider pluggable so a local LLM can be swapped in later without major refactoring.

---

## Business problem (summary of slides)

<div align="center">

![Cybersecurity Assessment & Authorisation Problem](images/use_case_slide_1.png)

![Opportunity Placemat](images/use_case_slide_2.png)

</div>

Large organisations that must accredit ICT systems face long lead times and backlogs for assessment and authorisation. Early triage is mostly manual, causing:

- Significant delays to capability availability (weeks to months).
- Heightened exposure to cybersecurity risks while waiting.
- Many rework loops because evidence is incomplete or inconsistent.

The proposed opportunity is to augment the earliest step (Engage Business / pre‑assessment) with an AI assistant that can:

- Check documentation completeness and basic maturity.
- Detect contradictions and obvious quality issues early.
- Highlight likely control gaps against a provided ruleset.
- Produce a concise, structured summary to accelerate human decision-making.

---

## Scope for interns

Build an API-first prototype that:

1) Calls an LLM over API (assume OpenAI gpt‑4o‑mini) using a provided key.
2) Converts common document formats (DOCX/PDF) to text reliably (via Pandoc).
3) Runs small, deterministic analyses (word counts, duplicates) to validate the pipeline.
4) Progresses to contradiction detection within an SSP sample.
5) Incorporates a subset, then the full set, of instructions and ISM rules to drive a rules‑aware analysis.
6) Presents results via a simple interface (CLI first; UI optional later).

Privacy note: Do not send sensitive or classified material to external APIs. Use synthetic/redacted SSP content unless explicitly cleared. Apply redaction where needed.

---

## Milestones, deliverables, and acceptance criteria

The following milestones map directly to the objectives provided. Each milestone lists an acceptance test and artefacts to check into the repo.

### Milestone 1 — Hello, GPT‑4o mini (API)
- Goal: Ask a hardcoded question to gpt‑4o‑mini via API and print the answer to console.
- Acceptance:
  - A Python script reads the API key from env vars and prints a non‑empty response.
  - Model, base URL, and temperature are configurable via env vars.
- Artefacts:
  - `src/hello_llm.py`
  - `docs/api_llm_setup.md` (or the setup section below)

### Milestone 2 — Text analytics on a plain text file
- Goal: Provide a lump of text (e.g., 500 animal names with duplicates) and ask a simple analytical question.
- Example prompts:
  - “How many times does the word ‘giraffe’ appear?”
  - “List all duplicated words and their counts.”
- Acceptance:
  - Deterministic results (same input → same output) and a printed JSON block with counts.
- Artefacts:
  - `data/animals.txt`
  - `src/analyze_text.py` with `--question` and `--file` flags; emits JSON.

### Milestone 3 — Reliable DOCX → text conversion (Pandoc)
- Goal: Convert a simple Word document (e.g., animals.docx) to text, repeat Milestone 2, and compare outputs.
- Acceptance:
  - DOCX→TXT pipeline produces the same counts as the original TXT.
  - A small test asserts equality of results.
- Artefacts:
  - `data/animals.docx`, generated TXT in `artifacts/animals.txt`
  - `src/convert_doc.py` and `tests/test_animals_equivalence.py`

### Milestone 4 — Contradiction detection on SSP (first 3 pages)
- Goal: Insert clearly contradictory statements (e.g., “sun rises in the east” vs “sun rises in the west”). Ask the LLM to detect contradictions.
- Acceptance:
  - Model returns a structured list of contradictions with line/section references where possible.
  - JSON schema adhered to (see “Output contract”).
- Artefacts:
  - `data/ssp_sample_p3.docx` (or PDF) + converted TXT in `artifacts/`
  - `src/find_contradictions.py`

### Milestone 5 — Rules‑aware analysis with partial instructions + ISM rules
- Goal: Provide a small curated subset of instructions and ISM rules; ask model to detect gaps/contradictions relative to that subset.
- Acceptance:
  - Output separates: (a) contradictions, (b) rule‑violations, (c) unknown/insufficient-evidence items.
  - Evidence snippets included for each finding.
- Artefacts:
  - `rules/instructions_sample.md`, `rules/ism_sample.md`
  - `src/analyze_ssp_rules.py`

### Milestone 6 — Full SSP + full instructions + all ISM rules
- Goal: Scale up the previous step to broader coverage.
- Acceptance:
  - Script completes within a reasonable time on a laptop (target: under 5 minutes; document actual time).
  - Summaries remain structured and machine‑readable; add a CSV export.
- Artefacts:
  - `data/ssp_full.(docx|pdf)`, `rules/instructions_full.md`, `rules/ism_full.md`
  - `src/run_full_assessment.py`, `artifacts/assessment_summary.json`, `.csv`

### Milestone 7 — Wrap in a simple app (UI options below)
- Goal: Convert the Python workflow into an interactive app (file upload → results view).
- Acceptance:
  - Run locally; selects model/ruleset; outputs human‑readable summary plus downloadable JSON/CSV.
- Artefacts:
  - See “UI options” for choices; prefer the simplest path first.

### Milestone 8 — Demonstrate the app
- Goal: Short demo with one clean “happy path” and one “edge case” (e.g., missing evidence).
- Acceptance:
  - Demo script in README; a short video or GIF is a plus.

---

## Output contract (for Milestones 4–6)

Return a single JSON object:

```json
{
  "document_id": "string",
  "summary": "one-paragraph high-level findings",
  "contradictions": [
    {"id": "c1", "statement_a": "text", "statement_b": "text", "locations": ["p2: s1", "p4: s3"], "confidence": 0.0}
  ],
  "rule_violations": [
    {"id": "r1", "rule_ref": "ISM-XX.123", "finding": "text", "evidence": "snippet", "confidence": 0.0}
  ],
  "insufficient_evidence": [
    {"control": "control-id-or-rule", "reason": "what is missing"}
  ]
}
```

Notes:
- Use low‑temperature generation and explicit instructions to minimise hallucinations.
- Prefer small, direct prompts; chain simple steps (extract → check → summarise).

---

## Technical approach (minimal pipeline)

1) Ingest
- Accept DOCX/PDF; convert to text via Pandoc; store the canonical TXT in `artifacts/`.

2) Chunk (optional at first)
- For long SSPs, split by headings/sections to keep prompts small.

3) Prompting patterns
- Use a deterministic style: “You are verifying contradictions. Only return JSON per schema. If unsure, put items in `insufficient_evidence`.”

4) Rules integration
- Load instructions/ISM rules as either: (a) appended context in prompt, or (b) pre‑indexed small knowledge base to retrieve the top‑k relevant rules (RAG; optional stretch).

5) Evaluation
- Track precision/recall on seeded contradictions; log latency and token counts if available.

---

## API setup on Windows (PowerShell)

Use a hosted LLM API (assume OpenAI for now) and Pandoc for conversions.

Pandoc (for DOCX/PDF → TXT):
- Install: `winget install JohnMacFarlane.Pandoc`

Python environment (example):
- Create venv and install basics
  - `py -m venv .venv`
  - `.\\.venv\\Scripts\\Activate.ps1`
  - `python -m pip install -U pip`
  - `pip install openai requests typer rich`
- Optional (for UIs later): `pip install gradio streamlit fastapi uvicorn textual`

Configuration (env vars):
- `OPENAI_API_KEY=***` (provided to interns)
- `WATCHTOWER_LLM_PROVIDER=openai`
- `WATCHTOWER_LLM_MODEL=gpt-4o-mini`
- Optional overrides: `OPENAI_BASE_URL` (for gateways), `WATCHTOWER_TEMPERATURE=0.1`, `WATCHTOWER_MAX_OUTPUT_TOKENS=800`

Cost and rate-limit guardrails:
- Keep temperature low (0.0–0.2) for determinism.
- Constrain max output tokens; prefer structured JSON.
- Batch long documents into sections; avoid sending full SSP in one prompt.
- Consider simple response caching during development to limit spend.

---

## UI options (Streamlit and alternatives)

Start with CLI, then pick one of:

- Gradio (simple web UI; already familiar in notebooks)
  - Pros: fast to prototype, file upload components, nice for demos
  - Cons: less control over production concerns

- Streamlit (data‑app UI)
  - Pros: dead-simple UI building, good widgets, quick deploys
  - Cons: fewer routing/layout primitives; larger footprint

- FastAPI + HTMX (lightweight web)
  - Pros: explicit routes, great APIs, progressive enhancement with minimal JS
  - Cons: slightly more plumbing than Streamlit/Gradio

- Flask or Dash (classic Python web options)
  - Pros: very widely used, lots of examples
  - Cons: more boilerplate for file uploads and state

- Textual (rich TUI)
  - Pros: runs entirely in terminal, great for air‑gapped demos, tiny footprint
  - Cons: no browser UI; not ideal for non-technical users

Recommendation:
- Phase 1–2: CLI only (deterministic testing).
- Phase 3–4: Gradio or Streamlit for fast file-upload UI.
- If time permits: FastAPI + HTMX for finer control and a REST endpoint.

---

## Risks and constraints

- Data sensitivity: use synthetic or redacted SSP content unless explicitly cleared; treat all uploads as confidential; never include keys in code.
- Accuracy vs. confidence: the model may miss contradictions; capture confidence and add human-in-the-loop.
- Determinism: prefer smaller prompts, fixed temperature, and explicit schemas; include seed examples sparingly.
- Cost/latency: budget tokens; log prompt and completion token counts; throttle to avoid rate limits.

---

## Stretch goals (optional)

- Retrieval‑Augmented Generation (RAG) over the ISM ruleset (e.g., simple BM25 or local embedding search).
- Automated evaluation harness with seeded contradictions and per‑rule checks.
- Export to a short “Assessment Report” PDF with a 1‑page executive summary.
- Caching of conversions and model calls to speed up iterative runs.

---

## What to submit

- Source code in `src/` with small, composable scripts.
- Sample data/rules (synthetic or redacted) in `data/` and `rules/`.
- Artifacts (converted text, JSON findings, CSV exports) in `artifacts/`.
- Short README with setup and a 2–3 minute demo script.

This prototype should make the earliest gate (“Engage Business” / SSP readiness) faster by surfacing contradictions, missing evidence, and likely rule violations before manual review.
