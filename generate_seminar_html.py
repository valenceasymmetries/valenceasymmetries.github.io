#!/usr/bin/env python3
"""
Generate HTML listing of PDFs under a docs directory, grouped by arbitrary subfolders.

Usage:
    python generate_seminar_html.py [--root ROOT_DIR] [--output OUTPUT_FILE]

Defaults:
    --root   ./doc
    --output ./seminars.html

Directory structure assumed:
  root/
    CATEGORY/
      SUBCATEGORY/
        file.pdf

No category or subcategory names are hard-coded; any names will work.
"""

import argparse
from pathlib import Path
from collections import defaultdict


def collect_files(root: Path):
    """
    Walk through root and collect PDF files, grouped by:
      category (first-level subdir) -> subcategory (second-level subdir) -> list of file paths

    Works for any names of category/subcategory folders.
    """
    structure = defaultdict(lambda: defaultdict(list))

    for path in root.rglob("*.pdf"):
        rel = path.relative_to(root)
        parts = rel.parts

        # Require at least: category / subcategory / file.pdf
        if len(parts) < 3:
            continue

        category, subcategory, filename = parts[0], parts[1], parts[2]
        structure[category][subcategory].append(path)

    # Sort files within each subcategory
    for category in structure:
        for subcategory in structure[category]:
            structure[category][subcategory].sort(key=lambda p: p.name.lower())

    return structure


def make_name_from_path(path: Path) -> str:
    """
    Given a file path like .../Bavolar.pdf, return 'Bavolar'.
    Customize here if you want more complex parsing.
    """
    return path.stem


def make_href_from_path(path: Path, root: Path) -> str:
    """
    Create an href relative to where the HTML will be served.
    Assumes the docs directory is accessible as 'docs/...' in URLs.
    Adjust the 'docs' prefix if your setup uses something else.
    """
    rel = path.relative_to(root)
    return str(Path("docs") / rel)


def generate_html(structure, root: Path) -> str:
    lines = []
    lines.append("<!DOCTYPE html>")
    lines.append("<html>")
    lines.append("<head>")
    lines.append("  <meta charset='UTF-8'>")
    lines.append("  <title>Seminar Presentations</title>")
    lines.append("  <style>")
    lines.append("    body { font-family: sans-serif; margin: 2rem; }")
    lines.append("    h1, h2, h3 { margin-top: 1.5rem; }")
    lines.append("    details { margin: 0.4rem 0; }")
    lines.append("    .speaker-info { margin-left: 1rem; }")
    lines.append("    .embed-container a { text-decoration: none; }")
    lines.append("  </style>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append("<h1>Seminar Presentations</h1>")

    # Sort categories and subcategories alphabetically; remove sorting if you prefer filesystem order
    for category in sorted(structure.keys()):
        subcats = structure[category]
        lines.append(f"<h2>{category}</h2>")

        for subcategory in sorted(subcats.keys()):
            files = subcats[subcategory]
            lines.append(f"<h3>{subcategory}</h3>")

            for file_path in files:
                name = make_name_from_path(file_path)
                href = make_href_from_path(file_path, root)

                summary_text = name  # customize here if needed

                lines.append("  <details>")
                lines.append(f"    <summary>{summary_text}</summary>")
                lines.append("    <div class=\"speaker-info\">")
                lines.append("      <div class=\"embed-container\">")
                lines.append(f"        <a href=\"{href}\" target=\"_blank\">Slides</a>")
                lines.append("      </div>")
                lines.append("    </div>")
                lines.append("  </details>")

    lines.append("</body>")
    lines.append("</html>")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate HTML listing of PDFs under a docs directory."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("doc"),
        help="Root directory to scan (default: ./doc). Change to ./docs if needed.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("seminars.html"),
        help="Output HTML file (default: ./seminars.html)",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Root directory not found: {root}")

    structure = collect_files(root)
    html = generate_html(structure, root)

    args.output.write_text(html, encoding="utf-8")
    print(f"HTML written to: {args.output.resolve()}")


if __name__ == "__main__":
    main()