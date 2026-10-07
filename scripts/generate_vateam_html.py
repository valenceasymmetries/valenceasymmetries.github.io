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
#
# YEAR-MONTH-CONFERENCE-extra-information.pdf
#
# Examples:
# 2026-06-PLM-talk-Slursarepernicious.pdf
# 2026-04-TSAcolloquium-talk-moralthoughtsharing.pdf
# 2026-03-UCL-talk-axiologicallyopposedadjectives.pdf
#
# The link text will be:
# PLM
# TSAcolloquium
# UCL
# ============================================================

def parse_filename(path):

    parts = path.stem.split("-")

    if len(parts) < 3:
        return None

    year = parts[0]
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

        info = parse_filename(pdf)

        if info is None:
            continue

        # Directory relative to root
        relative_parent = pdf.parent.relative_to(root)

        structure[str(relative_parent)].append(
            (pdf, info)
        )

    return structure


# ============================================================
# Get top-level team member directories
# ============================================================

def get_team_members(root):

    return sorted(
        [
            directory
            for directory in root.iterdir()
            if directory.is_dir()
        ],
        key=lambda p: p.name.lower()
    )


# ============================================================
# Get all PDFs belonging to one team member
# ============================================================

def get_team_member_files(
    team_member,
    root
):

    files = []

    for pdf in team_member.rglob("*.pdf"):

        info = parse_filename(pdf)

        if info is not None:
            files.append(
                (pdf, info)
            )

    return files


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
# Generate HTML for one team member
# ============================================================

def generate_team_member_html(
    team_member,
    root,
    output_path
):

    html = []

    files = get_team_member_files(
        team_member,
        root
    )

    # --------------------------------------------------------
    # Group PDFs by year
    # --------------------------------------------------------

    years = defaultdict(list)

    for pdf_path, info in files:

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
        # YEAR DETAILS
        # ====================================================

        html.append(
            '        <details class="subsection">'
        )

        html.append(
            f'          <summary>{year}'
        )

        html.append(
            '            <span class="caret"></span>'
        )

        html.append(
            '          </summary>'
        )

        html.append(
            ''
        )

        html.append(
            '          <div class="speaker-info">'
        )

        # ----------------------------------------------------
        # Files within year
        # ----------------------------------------------------

        year_files = sorted(
            years[year],
            key=lambda item: (
                item[1]["conference"].lower(),
                item[0].name.lower()
            )
        )

        for pdf_path, info in year_files:

            href = make_href(
                pdf_path,
                output_path
            )

            conference = info["conference"]

            html.append(
                f'            <div><a href="{href}">'
                f'{conference}'
                f'</a></div>'
            )

        html.append(
            '          </div>'
        )

        html.append(
            '        </details>'
        )

        html.append(
            ''
        )

    return "\n".join(html)


# ============================================================
# Generate complete HTML page
# ============================================================

def generate_html(
    root,
    output_path
):

    html = []

    # ========================================================
    # HTML HEADER
    # ========================================================

    html.append(
        '<!DOCTYPE html>'
    )

    html.append(
        '<html lang="en">'
    )

    html.append(
        '<head>'
    )

    html.append(
        '  <meta charset="UTF-8">'
    )

    html.append(
        '  <meta name="viewport" '
        'content="width=device-width, initial-scale=1.0">'
    )

    html.append(
        '  <title>VA Team</title>'
    )

    # Existing stylesheet
    html.append(
        '  <link rel="stylesheet" href="style.css">'
    )

    html.append(
        '</head>'
    )

    html.append(
        '<body>'
    )

    html.append(
        ''
    )

    # ========================================================
    # VA TEAM — OUTER DETAILS
    # ========================================================

    html.append(
        '<details>'
    )

    html.append(
        '  <summary class="details-summary">'
    )

    html.append(
        '    VA Team'
    )

    html.append(
        '    <span class="caret"></span>'
    )

    html.append(
        '  </summary>'
    )

    html.append(
        ''
    )

    # ========================================================
    # TEAM MEMBERS
    # ========================================================

    team_members = get_team_members(root)

    for team_member in team_members:

        html.append(
            '      <details class="subsection">'
        )

        html.append(
            f'        <summary>{team_member.name}'
        )

        html.append(
            '          <span class="caret"></span>'
        )

        html.append(
            '        </summary>'
        )

        html.append(
            ''
        )

        html.append(
            '        <div class="speaker-info">'
        )

        # ----------------------------------------------------
        # Years + conference links
        # ----------------------------------------------------

        team_member_html = generate_team_member_html(
            team_member,
            root,
            output_path
        )

        if team_member_html:
            html.append(
                team_member_html
            )

        html.append(
            '        </div>'
        )

        html.append(
            ''
        )

        html.append(
            '      </details>'
        )

        html.append(
            ''
        )

    # ========================================================
    # CLOSE VA TEAM DETAILS
    # ========================================================

    html.append(
        '  </details>'
    )

    html.append(
        ''
    )

    html.append(
        '</body>'
    )

    html.append(
        '</html>'
    )

    # ========================================================
    # Write HTML
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
            "Generate VA Team HTML from team-member "
            "PDF directories."
        )
    )

    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Root directory containing team member folders."
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output HTML file."
    )

    args = parser.parse_args()

    root = args.root.resolve()
    output = args.output.resolve()

    if not root.exists():

        raise FileNotFoundError(
            f"Root directory does not exist: {root}"
        )

    if not root.is_dir():

        raise NotADirectoryError(
            f"Root path is not a directory: {root}"
        )

    generate_html(
        root,
        output
    )

    print(
        f"Generated: {output}"
    )


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":
    main()