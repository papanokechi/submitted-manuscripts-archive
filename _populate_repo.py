#!/usr/bin/env python3
"""
Populate submitted-manuscripts from local manuscripts + submission log.

This script:
  1. Parses submission_log.txt into structured entries
  2. Scans the manuscript directory for PDFs
  3. Aligns log entries ↔ PDFs (best-effort filename + title matching)
  4. Generates <SHORT_NAME>/ folders at repo root with metadata JSON
  5. Copies manuscript PDFs (and .tex/.docx sources when available)
  6. Produces an alignment report
"""

import json, os, re, shutil, pathlib, textwrap, datetime

# ── Paths ──────────────────────────────────────────────────────────────
SRC_DIR   = pathlib.Path(r"C:\Users\shkub\OneDrive\Documents\archive\admin\VSCode\claude-chat\tex\submitted")
REPO_DIR  = pathlib.Path(r"C:\Users\shkub\OneDrive\Documents\archive\admin\VSCode\claude-chat\submitted-manuscripts-archive")
# NOTE: local clone folder kept as-is; GitHub repo is papanokechi/submitted-manuscripts
LOG_FILE  = SRC_DIR / "submission_log.txt"
MAN_DIR   = REPO_DIR  # manuscripts live at repo root
SCRIPT_DIR = REPO_DIR / "SCRIPTS"

# ── Helpers ────────────────────────────────────────────────────────────
def kebab(title: str) -> str:
    """Convert a title to a short kebab-case identifier."""
    # Remove LaTeX-style spacing artefacts (run-together words)
    t = re.sub(r'([a-z])([A-Z])', r'\1 \2', title)
    t = re.sub(r'[^a-zA-Z0-9\s-]', '', t)
    words = t.lower().split()
    # Keep first 6 meaningful words
    stop = {'a', 'an', 'the', 'of', 'in', 'for', 'and', 'on', 'to', 'from', 'with'}
    kept = [w for w in words if w not in stop][:6]
    return '-'.join(kept) if kept else 'untitled'


def parse_submission_log(path: pathlib.Path) -> list[dict]:
    """Parse the free-form submission log into structured entries."""
    text = path.read_text(encoding='utf-8')
    entries = []
    # Split on numbered entries: "1. Filename: ..."
    blocks = re.split(r'\n\s*\d+\.\s+Filename:', text)
    for block in blocks[1:]:  # skip header
        lines = block.strip().splitlines()
        entry = {
            'filename': '',
            'title': '',
            'venue': '',
            'status': '',
            'submission_id': '',
            'submission_date': '2026',  # default from log header
            'notes': '',
        }
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            if i == 0 and not line.startswith(('Title:', 'Status:', 'Submission')):
                entry['filename'] = line.strip()
                continue
            if line.startswith('Filename:'):
                entry['filename'] = line.split(':', 1)[1].strip()
            elif line.startswith('Title:'):
                entry['title'] = line.split(':', 1)[1].strip()
            elif line.startswith('Status:'):
                full = line.split(':', 1)[1].strip()
                # Extract venue from "Submitted to VENUE" or "Published on VENUE"
                m = re.match(r'(Submitted to|Published on)\s+(.+?)(?:\s*\(.*\))?$', full)
                if m:
                    entry['venue'] = m.group(2).strip()
                    entry['status'] = full
                else:
                    entry['status'] = full
                    entry['venue'] = full
            elif line.startswith('Submission ID:'):
                entry['submission_id'] = line.split(':', 1)[1].strip()
        # Derive short_name
        entry['short_name'] = kebab(entry['title'])
        # Derive year
        date_m = re.search(r'(20\d{2})', entry.get('submission_date', ''))
        entry['year'] = date_m.group(1) if date_m else '2026'
        entries.append(entry)
    return entries


def find_best_pdf(entry: dict, available: dict[str, pathlib.Path]) -> pathlib.Path | None:
    """Find the best matching PDF for a log entry among available files."""
    log_fn = entry['filename']
    # Direct match
    if log_fn in available:
        return available[log_fn]
    # Fuzzy: check if any available file contains most words from the title
    title_words = set(re.findall(r'[a-z]+', entry['title'].lower()))
    best_score, best_path = 0, None
    for fn, fp in available.items():
        if not fn.lower().endswith('.pdf'):
            continue
        fn_words = set(re.findall(r'[a-z]+', fn.lower()))
        score = len(title_words & fn_words)
        if score > best_score and score >= 2:
            best_score = score
            best_path = fp
    return best_path


# ── Main ───────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  Populating submitted-manuscripts")
    print("=" * 60)

    # 1) Parse log
    entries = parse_submission_log(LOG_FILE)
    print(f"\n[LOG] Parsed {len(entries)} entries from submission_log.txt")

    # 2) Scan available PDFs
    pdfs = {}
    all_files = {}
    for f in SRC_DIR.iterdir():
        all_files[f.name] = f
        if f.suffix.lower() == '.pdf':
            pdfs[f.name] = f
    print(f"[DIR] Found {len(pdfs)} PDFs in submitted/")

    # ── Manual filename → best-available-PDF mapping ──
    # (the log records original upload names; the directory has renamed copies)
    FILENAME_MAP = {
        'manuscript-r0.pdf': 'RatioUniversalityforMeinardus-ClassPartitionFunctions.pdf',
        'manuscript-r0 (1).pdf': 'ArithmeticSectorBifurcationinQuadratic.pdf',
        'manuscript-r0 (2).pdf': 'SpectralClassesofPolynomialContinuedFractions.pdf',
        'ai-behavior-science-v1.0.pdf': 'AI_Behavior_Science_Founding_Paper.pdf',
        'ZTEK_Paper9_v2.pdf': 'ZTEK_Paper9_v3_final.pdf',
        'CMF_Paper10_v2.pdf': 'CMF_Paper10_v3_final.pdf',
    }

    # 3) Align
    alignment = []  # (entry, pdf_path | None, status)
    used_pdfs = set()

    for entry in entries:
        log_fn = entry['filename']
        mapped_fn = FILENAME_MAP.get(log_fn, log_fn)
        pdf_path = pdfs.get(mapped_fn)
        if pdf_path is None:
            pdf_path = find_best_pdf(entry, pdfs)

        if pdf_path:
            used_pdfs.add(pdf_path.name)
            alignment.append((entry, pdf_path, 'OK'))
        else:
            alignment.append((entry, None, 'MISSING_PDF'))

    # Detect unmatched PDFs
    unmatched_pdfs = [n for n in pdfs if n not in used_pdfs]

    # 4) Build MANUSCRIPTS/ tree
    MAN_DIR.mkdir(parents=True, exist_ok=True)
    report_lines = []

    for entry, pdf_path, status in alignment:
        sn = entry['short_name']
        dest = MAN_DIR / sn
        dest.mkdir(parents=True, exist_ok=True)

        # Copy PDF
        if pdf_path and pdf_path.exists():
            shutil.copy2(pdf_path, dest / 'manuscript.pdf')
            report_lines.append(f"[OK] {sn}: aligned ({pdf_path.name})")
        else:
            report_lines.append(f"[MISSING PDF] {sn}: {entry['filename']}")

        # Copy companion .tex if exists
        if pdf_path:
            tex_name = pdf_path.stem + '.tex'
            tex_path = SRC_DIR / tex_name
            if tex_path.exists():
                shutil.copy2(tex_path, dest / 'source.tex')
            # Copy companion .docx
            docx_name = pdf_path.stem + '.docx'
            docx_path = SRC_DIR / docx_name
            if docx_path.exists():
                shutil.copy2(docx_path, dest / 'source.docx')

        # Derive DOI/arXiv
        doi_arxiv = ''
        sid = entry.get('submission_id', '')
        if 'DOI' in sid or 'doi' in sid or 'zenodo' in sid.lower():
            doi_arxiv = sid.replace('DOI ', 'https://doi.org/')
        elif sid:
            doi_arxiv = sid

        # Generate metadata JSON
        meta = {
            "title": entry['title'],
            "authors": "Shunsuke Kubota",
            "submitted_to": entry['venue'],
            "submission_date": entry['submission_date'],
            "submission_id": entry.get('submission_id', 'UNKNOWN'),
            "current_status": entry['status'],
            "doi_or_arxiv": doi_arxiv if doi_arxiv else "UNKNOWN",
            "keywords": [],
            "notes": entry.get('notes', ''),
            "original_filename": entry['filename'],
        }
        (dest / 'submission-metadata.json').write_text(
            json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8'
        )

    # ── Handle unmatched PDFs → create placeholder entries ──
    for uname in sorted(unmatched_pdfs):
        # Skip non-primary files (ancillary, anonymous, resubmissions, etc.)
        if any(skip in uname.lower() for skip in ['anonymous', 'ancillary', 'resubmission']):
            continue
        # Skip if it's a companion version of an already-matched paper
        sn = kebab(uname.replace('.pdf', ''))
        dest = MAN_DIR / sn
        if dest.exists():
            continue
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SRC_DIR / uname, dest / 'manuscript.pdf')
        meta = {
            "title": uname.replace('.pdf', '').replace('_', ' '),
            "authors": "Shunsuke Kubota",
            "submitted_to": "UNKNOWN",
            "submission_date": "UNKNOWN",
            "submission_id": "UNKNOWN",
            "current_status": "UNKNOWN",
            "doi_or_arxiv": "UNKNOWN",
            "keywords": [],
            "notes": "Auto-detected PDF with no matching log entry",
            "original_filename": uname,
        }
        (dest / 'submission-metadata.json').write_text(
            json.dumps(meta, indent=2, ensure_ascii=False), encoding='utf-8'
        )
        report_lines.append(f"[MISSING LOG] {sn}: {uname}")

    # Copy the submission log itself
    shutil.copy2(LOG_FILE, REPO_DIR / 'submission_log.txt')
    # Copy arxiv metadata
    arxiv_meta = SRC_DIR / 'arxiv_metadata.txt'
    if arxiv_meta.exists():
        shutil.copy2(arxiv_meta, REPO_DIR / 'arxiv_metadata.txt')

    # 5) Write alignment report
    report_text = '\n'.join(sorted(report_lines))
    (REPO_DIR / 'ALIGNMENT_REPORT.txt').write_text(report_text, encoding='utf-8')

    print(f"\n[DONE] Generated {len(alignment)} manuscript folders")
    print(f"[DONE] {len(unmatched_pdfs)} unmatched PDFs handled")
    print(f"\n{'=' * 60}")
    print("  ALIGNMENT REPORT")
    print('=' * 60)
    print(report_text)
    print('=' * 60)

    # Return data for downstream use
    return entries, alignment, unmatched_pdfs

if __name__ == '__main__':
    main()
