#!/usr/bin/env python3
"""
Generate HTML listing of PDFs under a docs directory.

HTML structure:

  VA Team
      YEAR
          CONFERENCE (MONTH)
              PDF files

PDF filenames are expected to follow:

    YEAR-MONTH-CONFERENCE.pdf

or:

    YEAR-MONTH-CONFERENCE-OTHER-INFORMATION.pdf

For example:

    2026-08-ESSLLI.pdf
    2026-08-ESSLLI-Course.pdf
    2025-07-CogSci-Talk.pdf

The first three hyphen-separated components are interpreted as:
    YEAR
    MONTH
    CONFERENCE

The numeric month is converted to its full name.

For example:

    2026-08-ESSLLI.pdf

becomes:

    ESSLLI (August)

Any additional information after the conference is ignored for
the conference heading, but the full filename is still used as
the individual PDF title.

Usage:
    python generate_vateam_html.py [--root ROOT_DIR] [--output OUTPUT_FILE]
    python generate_vateam_html.py \
  --root ../docs/VA_team_presentations \
  --output ../docs/VA_team_presentations/html_output.html

Defaults:
    --root   ./doc
    --output ./seminars.html
"""

from pathlib import Path
from collections import defaultdict
import argparse
import os


# ============================================================
# Parse PDF filename
#
# Expected format:
# YEAR-MONTH-CONFERENCE-extra-information.pdf
#
# Examples:
# 2026-08-ESSLLI.pdf
# 2026-08-ESSLLI-Course.pdf
#
# The link text will simply be:
# ESSLLI
# ============================================================

def parse_filename(path):
    parts = path.stem.split("-")

    if len(parts) < 3:
        return None

    year = parts[0]
    month = parts[1]
    conference = parts[2]

    return {
        "year": year,
        "conference": conference,
    }


# ============================================================
# Collect PDFs
# ============================================================

def collect_files(root):
    structure = defaultdict(list)

    for pdf in root.rglob("*.pdf"):

        relative_parent = pdf.parent.relative_to(root)

        info = parse_filename(pdf)

        if info is not None:
            structure[str(relative_parent)].append(
                (pdf, info)
            )

    return structure


# ============================================================
# Get all directories
# ============================================================

def get_all_directories(root):

    directories = []

    for directory in root.rglob("*"):

        if directory.is_dir():
            directories.append(directory)

    return sorted(
        directories,
        key=lambda p: str(p)
    )


# ============================================================
# Get immediate child directories
# ============================================================

def get_child_directories(
    directory,
    all_directories
):

    return sorted(
        [
            candidate
            for candidate in all_directories
            if candidate.parent == directory
        ],
        key=lambda p: p.name.lower()
    )


# ============================================================
# Create relative PDF link
# ============================================================

def make_href(
    pdf_path,
    output_path
):

    return os.path.relpath(
        pdf_path,
        output_path.parent
    ).replace(os.sep, "/")


# ============================================================
# Sort years newest first
# ============================================================

def year_sort_key(year):

    try:
        return -int(year)

    except ValueError:
        return year


# ============================================================
# Generate the contents for one team member
# ============================================================

def generate_team_member_html(
    directory,
    root,
    structure,
    output_path
):

    html = []

    # --------------------------------------------------------
    # Find all PDFs belonging to this team member
    # --------------------------------------------------------

    team_member_files = []

    for relative_directory, files in structure.items():

        relative_path = Path(relative_directory)

        # Is this directory inside the current team member?
        try:
            relative_path.relative_to(
                directory.relative_to(root)
            )

            team_member_files.extend(files)

        except ValueError:
            pass

    # --------------------------------------------------------
    # Group PDFs by year
    # --------------------------------------------------------

    years = defaultdict(list)

    for pdf_path, info in team_member_files:

        years[info["year"]].append(
            (pdf_path, info)
        )

    # --------------------------------------------------------
    # Years, newest first
    # --------------------------------------------------------

    sorted_years = sorted(
        years.keys(),
        key=year_sort_key
    )

    for year in sorted_years:

        # ====================================================
        # YEAR = collapsible
        # ====================================================

        html.append(
            '<details class="subsection">'
        )

        html.append(
            f"<summary>{year}</summary>"
        )

        html.append(
            '<div class="speaker-info">'
        )

        # ----------------------------------------------------
        # PDFs / conferences
        # ----------------------------------------------------

        year_files = sorted(
            years[year],
            key=lambda x: (
                x[1]["conference"].lower(),
                x[0].name.lower()
            )
        )

        for pdf_path, info in year_files:

            href = make_href(
                pdf_path,
                output_path
            )

            conference = info["conference"]

            html.append(
                f'<div>'
                f'<a href="{href}">'
                f'{conference}'
                f'</a>'
                f'</div>'
            )

        html.append(
            "</div>"
        )

        html.append(
            "</details>"
        )

    return "\n".join(html)


# ============================================================
# Generate complete HTML
# ============================================================

def generate_html(
    root,
    output_path
):

    structure = collect_files(root)

    all_directories = get_all_directories(root)

    html = []

    # ========================================================
    # HTML header
    # ========================================================

    html.append(
        "<!DOCTYPE html>"
    )

    html.append(
        '<html lang="en">'
    )

    html.append(
        "<head>"
    )

    html.append(
        '<meta charset="UTF-8">'
    )

    html.append(
        '<meta name="viewport" '
        'content="width=device-width, initial-scale=1.0">'
    )

    html.append(
        "<title>VA Team</title>"
    )

    # Your existing stylesheet
    html.append(
        '<link rel="stylesheet" href="style.css">'
    )

    html.append(
        "</head>"
    )

    html.append(
        "<body>"
    )

    # ========================================================
    # VA_team
    # ========================================================

    html.append(
        "<h2>VA_team</h2>"
    )

    # ========================================================
    # Team members
    # ========================================================

    team_members = [
        directory
        for directory in all_directories
        if directory.parent == root
    ]

    team_members = sorted(
        team_members,
        key=lambda p: p.name.lower()
    )

    for team_member in team_members:

        # ----------------------------------------------------
        # Team member = collapsible
        # ----------------------------------------------------

        html.append(
            '<details class="subsection">'
        )

        html.append(
            f"<summary>{team_member.name}</summary>"
        )

        html.append(
            '<div class="speaker-info">'
        )

        html.append(
            generate_team_member_html(
                team_member,
                root,
                structure,
                output_path
            )
        )

        html.append(
            "</div>"
        )

        html.append(
            "</details>"
        )

    # ========================================================
    # Close HTML
    # ========================================================

    html.append(
        "</body>"
    )

    html.append(
        "</html>"
    )

    # ========================================================
    # Write output
    # ========================================================

    output_path.write_text(
        "\n".join(html),
        encoding="utf-8"
    )


# ============================================================
# Main
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Generate VA Team HTML page "
            "from PDF directories."
        )
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=Path("doc"),
        help=(
            "Root directory containing "
            "team member folders."
        )
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("va_team.html"),
        help="Output HTML file."
    )

    args = parser.parse_args()

    root = args.root.resolve()

    output = args.output.resolve()

    if not root.exists():

        raise FileNotFoundError(
            f"Root directory does not exist: {root}"
        )

    generate_html(
        root,
        output
    )

    print(
        f"Generated: {output}"
    )


if __name__ == "__main__":
    main()