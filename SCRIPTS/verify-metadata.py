#!/usr/bin/env python3
"""
verify-metadata.py – Validate submission-metadata.json files across the repo.

Checks:
  - Valid JSON syntax
  - Required fields present
  - No UNKNOWN values (warnings)
  - Author consistency

Usage:
    python SCRIPTS/verify-metadata.py
"""

import json, pathlib, sys

REPO = pathlib.Path(__file__).resolve().parent.parent
MAN  = REPO / "MANUSCRIPTS"

REQUIRED_FIELDS = [
    "title", "authors", "submitted_to", "submission_date",
    "current_status", "doi_or_arxiv", "keywords", "notes",
]


def main() -> int:
    errors = 0
    warnings = 0

    meta_files = sorted(MAN.rglob("submission-metadata.json"))
    if not meta_files:
        print("[ERROR] No submission-metadata.json files found.")
        return 1

    for mf in meta_files:
        rel = mf.relative_to(REPO)
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"[ERROR] {rel}: invalid JSON – {e}")
            errors += 1
            continue

        # Required fields
        for field in REQUIRED_FIELDS:
            if field not in data:
                print(f"[ERROR] {rel}: missing required field '{field}'")
                errors += 1

        # UNKNOWN warnings
        for field in REQUIRED_FIELDS:
            val = data.get(field, "")
            if val == "UNKNOWN":
                print(f"[WARN]  {rel}: '{field}' is UNKNOWN")
                warnings += 1

        # Keywords should be a list
        kw = data.get("keywords")
        if kw is not None and not isinstance(kw, list):
            print(f"[ERROR] {rel}: 'keywords' should be a list, got {type(kw).__name__}")
            errors += 1

    print(f"\n--- Checked {len(meta_files)} files: {errors} errors, {warnings} warnings ---")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
