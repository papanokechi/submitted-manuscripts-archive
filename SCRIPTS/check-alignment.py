#!/usr/bin/env python3
"""
check-alignment.py – Compare MANUSCRIPTS/ tree against submission_log.txt.

Produces a human + machine readable alignment report.

Usage:
    python SCRIPTS/check-alignment.py
"""

import json, pathlib, re, sys

REPO   = pathlib.Path(__file__).resolve().parent.parent
MAN    = REPO / "MANUSCRIPTS"
LOG    = REPO / "submission_log.txt"


def load_log_titles(log_path: pathlib.Path) -> dict[str, str]:
    """Return {normalised_title: raw_title} from submission_log.txt."""
    text = log_path.read_text(encoding="utf-8")
    titles = {}
    for m in re.finditer(r"Title:\s*(.+)", text):
        raw = m.group(1).strip()
        norm = re.sub(r"\s+", " ", raw).lower()
        titles[norm] = raw
    return titles


def scan_manuscripts(man_dir: pathlib.Path) -> list[dict]:
    """Walk MANUSCRIPTS/<SHORT>/ and return metadata dicts."""
    results = []
    for meta_file in sorted(man_dir.rglob("submission-metadata.json")):
        data = json.loads(meta_file.read_text(encoding="utf-8"))
        data["_dir"] = meta_file.parent
        data["_has_pdf"] = (meta_file.parent / "manuscript.pdf").exists()
        results.append(data)
    return results


def main() -> int:
    if not LOG.exists():
        print("[ERROR] submission_log.txt not found at repo root.")
        return 1

    log_titles = load_log_titles(LOG)
    manuscripts = scan_manuscripts(MAN)

    ok = miss_log = miss_pdf = field_warn = 0
    lines = []

    for ms in manuscripts:
        rel = ms["_dir"].relative_to(REPO)
        title_norm = re.sub(r"\s+", " ", ms.get("title", "")).lower()

        if not ms["_has_pdf"]:
            lines.append(f"[MISSING PDF] {rel}")
            miss_pdf += 1
        elif title_norm not in log_titles and ms.get("notes", "") == "Auto-detected PDF with no matching log entry":
            lines.append(f"[MISSING LOG] {rel}")
            miss_log += 1
        else:
            # Field completeness check
            missing = [k for k in ("submitted_to", "submission_date", "current_status")
                       if ms.get(k, "UNKNOWN") == "UNKNOWN"]
            if missing:
                lines.append(f"[FIELD WARNING] {rel}: missing {', '.join(missing)}")
                field_warn += 1
            else:
                lines.append(f"[OK] {rel}")
                ok += 1

    lines.sort()
    print("\n".join(lines))
    print(f"\n--- Summary: {ok} OK, {miss_log} missing log, {miss_pdf} missing PDF, {field_warn} field warnings ---")
    return 0 if (miss_pdf == 0 and miss_log == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
