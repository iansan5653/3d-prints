#!/usr/bin/env python3

import argparse
import subprocess
import sys
from pathlib import Path

import cairosvg


REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
OUTPUT_EXTENSIONS = (".3mf", ".stl", ".svg")
PREVIEW_DIRECTORY = REPOSITORY_ROOT / ".render-model-previews"


def model_path(value: str) -> Path:
    candidate = Path(value)
    if candidate.suffix == "":
        candidate = candidate.with_suffix(".py")

    path = (REPOSITORY_ROOT / candidate).resolve()
    if path.parent != REPOSITORY_ROOT:
        raise argparse.ArgumentTypeError(
            "model must be a root-level Python file in this repository"
        )
    if path.name == "utils.py" or path.suffix != ".py" or not path.is_file():
        raise argparse.ArgumentTypeError(f"not a model file: {value}")
    if "show_or_export" not in path.read_text():
        raise argparse.ArgumentTypeError(
            f"{path.name} does not call show_or_export"
        )
    return path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render a repository build123d model and validate its exports."
    )
    parser.add_argument("model", type=model_path)
    parser.add_argument(
        "--open",
        action="store_true",
        help="open the generated PNG preview in VS Code",
    )
    args = parser.parse_args()

    subprocess.run(
        [sys.executable, args.model.name],
        cwd=REPOSITORY_ROOT,
        check=True,
    )

    output_dir = REPOSITORY_ROOT / "output" / args.model.stem
    artifacts = [
        output_dir / f"{args.model.stem}{extension}"
        for extension in OUTPUT_EXTENSIONS
    ]
    missing = [path for path in artifacts if not path.is_file() or path.stat().st_size == 0]
    if missing:
        parser.error(
            "model did not produce non-empty artifacts: "
            + ", ".join(str(path.relative_to(REPOSITORY_ROOT)) for path in missing)
        )

    PREVIEW_DIRECTORY.mkdir(parents=True, exist_ok=True)
    preview = PREVIEW_DIRECTORY / f"{args.model.stem}.png"
    cairosvg.svg2png(
        url=str(artifacts[-1]),
        write_to=str(preview),
        background_color="white",
        scale=4,
    )
    if not preview.is_file() or preview.stat().st_size == 0:
        parser.error(f"failed to create PNG preview: {preview}")

    print("Validated artifacts:")
    for artifact in artifacts:
        print(f"  {artifact.relative_to(REPOSITORY_ROOT)}")
    print(f"Preview PNG: {preview}")

    if args.open:
        subprocess.run(
            ["code", "--reuse-window", str(preview)],
            cwd=REPOSITORY_ROOT,
            check=True,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
