# submitted-manuscripts-archive

Private archive of submitted academic manuscripts by **Shunsuke Kubota**.

## Purpose

Reproducible, version-controlled record of every manuscript submission —
PDFs, source files, metadata, and alignment checks — in a single place.

## Directory structure

```
MANUSCRIPTS/
  <short-name>/
    manuscript.pdf          ← submitted PDF
    source.tex              ← LaTeX source (if available)
    source.docx             ← Word source (if available)
    submission-metadata.json← structured metadata
    supplementary/          ← supplementary material (if any)

SCRIPTS/
  check-alignment.py   ← compare MANUSCRIPTS/ vs submission_log.txt
  verify-metadata.py   ← validate JSON schema & field completeness
  build-index.py       ← generate MANUSCRIPTS_INDEX.md table

submission_log.txt     ← authoritative submission log (source of truth)
arxiv_metadata.txt     ← arXiv upload metadata
ALIGNMENT_REPORT.txt   ← latest alignment report
MANUSCRIPTS_INDEX.md   ← auto-generated table of all manuscripts
```

## How alignment works

1. `_populate_repo.py` parses `submission_log.txt` into structured entries.
2. Each entry is matched to a PDF in the source directory by filename (with a
   manual map for renamed files) or by fuzzy title matching.
3. Matched pairs are copied into `MANUSCRIPTS/<short-name>/` with a
   generated `submission-metadata.json`.
4. Unmatched PDFs get placeholder metadata with `"UNKNOWN"` fields.
5. Unmatched log entries (no PDF found) are flagged as `[MISSING PDF]`.

## How to run scripts

```bash
# From repo root:
python SCRIPTS/check-alignment.py    # alignment report
python SCRIPTS/verify-metadata.py    # metadata validation
python SCRIPTS/build-index.py        # rebuild MANUSCRIPTS_INDEX.md
```

## Metadata schema

Each `submission-metadata.json` contains:

| Field             | Type     | Description                        |
|-------------------|----------|------------------------------------|
| title             | string   | Full manuscript title              |
| authors           | string   | Author list                        |
| submitted_to      | string   | Journal / venue                    |
| submission_date   | string   | Date of submission                 |
| submission_id     | string   | Journal tracking ID or DOI         |
| current_status    | string   | Submitted / Published / Rejected   |
| doi_or_arxiv      | string   | DOI or arXiv link if available     |
| keywords          | string[] | Subject keywords                   |
| notes             | string   | Free-form notes                    |
| original_filename | string   | Original filename from log         |

## Re-populating

To regenerate the entire tree from scratch:

```bash
python _populate_repo.py
python SCRIPTS/build-index.py
python SCRIPTS/check-alignment.py
python SCRIPTS/verify-metadata.py
```

## License

This repository is **private**. Contents are not licensed for redistribution.
