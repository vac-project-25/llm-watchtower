# API and Environment Setup (Windows PowerShell)

Follow these steps to prepare your machine for Watchtower development.

## 1) Install Pandoc (for DOCX/PDF → TXT)

- Install via winget:

```powershell
winget install JohnMacFarlane.Pandoc
```

Verify it works:

```powershell
pandoc --version
```

## 2) Create a Python virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
```

## 3) Install Python dependencies

```powershell
pip install -r requirements.txt
```

Packages include: requests, typer, rich, pytest (and optionally openai if you prefer using the SDK).

## 4) Configure environment variables

Set in the same PowerShell session (temporary):

```powershell
$env:OPENAI_API_KEY = "<your-key>"
$env:WATCHTOWER_LLM_PROVIDER = "openai"
$env:WATCHTOWER_LLM_MODEL = "gpt-4o-mini"
$env:WATCHTOWER_TEMPERATURE = "0.1"
$env:WATCHTOWER_MAX_OUTPUT_TOKENS = "800"
# Optional gateway/base URL
# $env:OPENAI_BASE_URL = "https://your-gateway.example.com/v1"
```

To make them persistent, add them to your user environment variables in Windows, or create a small `.env.ps1` script and dot-source it when needed.

## 5) Quick smoke tests

- Milestone 1 (Hello LLM):

```powershell
python -m src.hello_llm --question "Give me one sentence about Watchtower."
```

- Milestone 2 (Deterministic analytics):

```powershell
python -m src.analyze_text --file data/animals.txt --question duplicates
python -m src.analyze_text --file data/animals.txt --question "count:giraffe"
```

- Milestone 3 (DOCX → TXT):

```powershell
python -m src.convert_doc --input data/animals.docx --output artifacts/animals.txt
```

If you see any issues with Pandoc, re-open your terminal or check PATH.
