#!/usr/bin/env python3
"""
update-dates-and-build-latest.py

1. Reads each submission-metadata.json
2. Looks up the original PDF's LastWriteTime from the source directory
3. Updates submission_date with the real file date
4. Generates the "Latest Submissions" section in MANUSCRIPTS_INDEX.md
"""

import json, os, pathlib, datetime

SRC_DIR  = pathlib.Path(r"C:\Users\shkub\OneDrive\Documents\archive\admin\VSCode\claude-chat\tex\submitted")
REPO_DIR = pathlib.Path(r"C:\Users\shkub\OneDrive\Documents\archive\admin\VSCode\claude-chat\submitted-manuscripts-archive")
MAN_DIR  = REPO_DIR / "MANUSCRIPTS"

# Build a lookup: filename → last-modified date (from source dir)
def build_date_lookup() -> dict[str, str]:
    lookup = {}
    for f in SRC_DIR.iterdir():
        if f.suffix.lower() == '.pdf':
            mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime)
            lookup[f.name] = mtime.strftime('%Y-%m-%d')
    return lookup


def main():
    date_lookup = build_date_lookup()
    print(f"[INFO] Built date lookup for {len(date_lookup)} PDFs\n")

    # Collect all manuscripts with updated dates
    manuscripts = []

    for meta_file in sorted(MAN_DIR.rglob("submission-metadata.json")):
        data = json.loads(meta_file.read_text(encoding='utf-8'))
        orig_fn = data.get('original_filename', '')

        # Try to find the real date
        real_date = None

        # Direct match
        if orig_fn in date_lookup:
            real_date = date_lookup[orig_fn]

        # Check mapped filenames (same map as _populate_repo.py)
        FILENAME_MAP = {
            'manuscript-r0.pdf': 'RatioUniversalityforMeinardus-ClassPartitionFunctions.pdf',
            'manuscript-r0 (1).pdf': 'ArithmeticSectorBifurcationinQuadratic.pdf',
            'manuscript-r0 (2).pdf': 'SpectralClassesofPolynomialContinuedFractions.pdf',
            'ai-behavior-science-v1.0.pdf': 'AI_Behavior_Science_Founding_Paper.pdf',
            'ZTEK_Paper9_v2.pdf': 'ZTEK_Paper9_v3_final.pdf',
            'CMF_Paper10_v2.pdf': 'CMF_Paper10_v3_final.pdf',
        }
        mapped = FILENAME_MAP.get(orig_fn)
        if mapped and mapped in date_lookup:
            real_date = date_lookup[mapped]

        # Fallback: check if any PDF in the folder's source matches
        if real_date is None:
            # Try matching by the manuscript.pdf that was copied
            ms_pdf = meta_file.parent / 'manuscript.pdf'
            if ms_pdf.exists():
                mtime = datetime.datetime.fromtimestamp(ms_pdf.stat().st_mtime)
                real_date = mtime.strftime('%Y-%m-%d')

        if real_date:
            old_date = data.get('submission_date', 'UNKNOWN')
            if old_date != real_date:
                print(f"[UPDATE] {meta_file.parent.name}: {old_date} → {real_date}")
                data['submission_date'] = real_date
                meta_file.write_text(
                    json.dumps(data, indent=2, ensure_ascii=False),
                    encoding='utf-8'
                )
        else:
            print(f"[SKIP]   {meta_file.parent.name}: no date found")

        # Collect for index
        rel_dir = meta_file.parent.relative_to(REPO_DIR).as_posix()
        manuscripts.append({
            'path': rel_dir,
            'title': data.get('title', 'UNKNOWN'),
            'date': data.get('submission_date', 'UNKNOWN'),
            'venue': data.get('submitted_to', 'UNKNOWN'),
            'status': data.get('current_status', 'UNKNOWN'),
            'sid': data.get('submission_id', ''),
            'doi': data.get('doi_or_arxiv', ''),
        })

    # Sort newest → oldest, then alphabetically by title for ties
    def sort_key(m):
        d = m['date'] if m['date'] != 'UNKNOWN' else '0000-00-00'
        return (-int(d.replace('-', '')), m['title'].lower())

    manuscripts.sort(key=sort_key)

    # ── Build MANUSCRIPTS_INDEX.md ──
    lines = [
        "# Manuscripts Index",
        "",
        f"*Auto-generated — {len(manuscripts)} manuscripts*",
        "",
        "## All Submissions (Newest → Oldest)",
        "",
    ]

    for m in manuscripts:
        pdf_link = f"{m['path']}/manuscript.pdf"
        folder_link = m['path']
        date_str = m['date'] if m['date'] != 'UNKNOWN' else '????-??-??'
        lines.append(
            f"- **{date_str}** — **{m['title']}**  "
        )
        lines.append(
            f"  [PDF]({pdf_link}) • [Folder]({folder_link})  "
        )
        lines.append(
            f"  *Status:* {m['status']} • *Venue:* {m['venue']}"
        )
        lines.append("")

    # Also append a summary table
    lines.extend([
        "---",
        "",
        "## Summary Table",
        "",
        "| # | Date | Title | Venue | Status |",
        "|---|------|-------|-------|--------|",
    ])
    for i, m in enumerate(manuscripts, 1):
        title_short = m['title'][:80] + ("…" if len(m['title']) > 80 else "")
        lines.append(
            f"| {i} | {m['date']} | {title_short} | {m['venue']} | {m['status']} |"
        )

    out_path = REPO_DIR / "MANUSCRIPTS_INDEX.md"
    out_path.write_text("\n".join(lines) + "\n", encoding='utf-8')
    print(f"\n[OK] Wrote {out_path.name} with {len(manuscripts)} entries (newest → oldest)")


if __name__ == '__main__':
    main()
