# Submitted Manuscripts

## ⭐ Featured Manuscript
**Resurgence Structure of Quadratic Polynomial Continued Fractions**
[PDF](painlev-iiid6-resurgence-constant-quadratic-polynomial/manuscript.pdf) • [Folder](painlev-iiid6-resurgence-constant-quadratic-polynomial/)

A representative submission highlighting the resurgence and asymptotic structure of quadratic polynomial continued fractions.

---

A version-controlled archive of all submitted research manuscripts
by **Shunsuke Kubota**.

Each manuscript lives in its own folder at the repository root and includes:

- `manuscript.pdf` — the submitted PDF
- `submission-metadata.json` — structured metadata
- `source.tex` / `source.docx` — source files (when available)
- `supplementary/` — supplementary materials (when available)

## All Submissions

See **[MANUSCRIPTS_INDEX.md](MANUSCRIPTS_INDEX.md)** for the complete list, newest → oldest.

## Directory structure

```
submitted-manuscripts/
  <short-name>/
    manuscript.pdf
    submission-metadata.json
    source.tex / source.docx
    supplementary/
  SCRIPTS/
  MANUSCRIPTS_INDEX.md
  README.md
  submission_log.txt
```

## Scripts

```bash
python SCRIPTS/check-alignment.py    # alignment report
python SCRIPTS/verify-metadata.py    # metadata validation
python SCRIPTS/build-index.py        # rebuild MANUSCRIPTS_INDEX.md
python _update_dates_and_build_latest.py  # update dates + rebuild index
python _populate_repo.py             # full re-populate from source dir
```

## Metadata schema

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

## License

This repository is **private**. Contents are not licensed for redistribution.
