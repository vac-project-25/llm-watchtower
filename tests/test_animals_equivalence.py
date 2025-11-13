import os
from pathlib import Path
import pytest


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _compute_counts(text: str):
    from src.analyze_text import compute_word_counts

    return compute_word_counts(text)


def test_animals_equivalence_docx_to_txt_matches_txt():
    # Requires data/animals.docx and Pandoc installed.
    txt_path = "data/animals.txt"
    docx_path = "data/animals.docx"
    if not os.path.exists(docx_path):
        pytest.skip("data/animals.docx not present; add it to run this test.")

    try:
        from src.convert_doc import convert_docx_to_txt
    except Exception:
        pytest.skip("Pandoc not available or converter import failed.")

    out_txt = "artifacts/animals_from_docx.txt"
    convert_docx_to_txt(docx_path, out_txt)

    a = _compute_counts(_read(txt_path))
    b = _compute_counts(_read(out_txt))
    assert a == b
