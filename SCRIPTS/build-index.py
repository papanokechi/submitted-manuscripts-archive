#!/usr/bin/env python3
"""
build-index.py – Generate MANUSCRIPTS_INDEX.md from submission-metadata.json files.

Creates a Markdown table of all manuscripts sorted by submission date.

Usage:
    python SCRIPTS/build-index.py
"""

import json, pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT  = REPO / "MANUSCRIPTS_INDEX.md"
SKIP_DIRS = {'.git', 'SCRIPTS', '__pycache__'}


def main():
    rows = []
    for d in sorted(REPO.iterdir()):
        if not d.is_dir() or d.name in SKIP_DIRS or d.name.startswith('.'):
            continue
        mf = d / "submission-metadata.json"
        if not mf.exists():
            continue
        data = json.loads(mf.read_text(encoding="utf-8"))
        rel_dir = mf.parent.relative_to(REPO).as_posix()
        rows.append({
            "path": rel_dir,
            "title": data.get("title", "UNKNOWN"),
            "venue": data.get("submitted_to", "UNKNOWN"),
            "date": data.get("submission_date", "UNKNOWN"),
            "status": data.get("current_status", "UNKNOWN"),
            "doi": data.get("doi_or_arxiv", ""),
            "sid": data.get("submission_id", ""),
        })

    # Sort by path (year/short_name)
    rows.sort(key=lambda r: r["path"])

    lines = [
        "# Manuscripts Index",
        "",
        f"*Auto-generated — {len(rows)} manuscripts*",
        "",
        "| # | Directory | Title | Venue | Status | ID |",
        "|---|-----------|-------|-------|--------|----|",
    ]
    for i, r in enumerate(rows, 1):
        title_short = r["title"][:80] + ("…" if len(r["title"]) > 80 else "")
        sid = r["doi"] if r["doi"] and r["doi"] != "UNKNOWN" else r["sid"]
        lines.append(
            f"| {i} | `{r['path']}` | {title_short} | {r['venue']} | {r['status']} | {sid} |"
        )

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK] Wrote {OUT.relative_to(REPO)} with {len(rows)} entries.")


if __name__ == "__main__":
    main()
