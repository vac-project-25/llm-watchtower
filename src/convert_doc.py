from __future__ import annotations

import subprocess
import shutil
from pathlib import Path
import typer


def convert_docx_to_txt(input_path: str, output_path: str) -> None:
    """Convert DOCX/PDF to plain text using pandoc."""
    pandoc = shutil.which("pandoc")
    if not pandoc:
        raise RuntimeError("Pandoc is not installed or not on PATH. Install via winget: winget install JohnMacFarlane.Pandoc")

    in_path = Path(input_path)
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [pandoc, "-s", str(in_path), "-t", "plain", "-o", str(out_path)]
    subprocess.run(cmd, check=True)


app = typer.Typer(add_completion=False, help="Milestone 3: DOCX/PDF -> TXT via Pandoc")


@app.command()
def main(
    input: str = typer.Option(..., "--input", "-i", help="Path to input .docx or .pdf"),
    output: str = typer.Option(..., "--output", "-o", help="Path to output .txt"),
):
    convert_docx_to_txt(input, output)
    typer.echo(f"Converted to: {output}")


if __name__ == "__main__":
    app()
