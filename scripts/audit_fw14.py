#!/usr/bin/env python3
"""Report reproducibility and provenance gaps in the FW 14.00 material.

This is deliberately a non-executing audit: it reads source text and metadata
only.  A non-empty report is expected while the research inputs are missing;
the exit status is reserved for audit/parser errors.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REQUIRED = (
    "README.md",
    "FW14_AUDIT.md",
    "FW14_FINDINGS.md",
    "1400_offsets.txt",
    "1400.c",
    "1400.h",
    "exploit.html",
    "jordy_stage2_1400.js",
    "webkit_gadgets_1400.js",
)

SYSENT_RE = re.compile(
    r"\bSYSENT(?:_addr)?\b\s*(?:=|:)\s*`?\s*(0x[0-9a-fA-F]+)", re.I
)


def line_number(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def finding(status: str, claim: str, path: str | None = None,
            line: int | None = None, detail: str = "") -> dict:
    return {
        "status": status,
        "claim": claim,
        "path": path,
        "line": line,
        "detail": detail,
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit(root: Path) -> dict:
    findings: list[dict] = []
    for relative in REQUIRED:
        if not (root / relative).is_file():
            findings.append(finding("BLOCKED", f"required audit input {relative}", relative,
                                    detail="file is absent from the repository layout"))

    # These include paths are part of the documented C build but are not in this checkout.
    for relative in ("sections.h", "offsets.h", "offsets/1400.h"):
        if not (root / relative).is_file():
            findings.append(finding("BLOCKED", f"build input {relative}", relative,
                                    detail="referenced by 1400.c/1400.h but absent"))

    source = {}
    for relative in ("1400.c", "1400_offsets.txt", "jordy_stage2_1400.js",
                     "webkit_gadgets_1400.js"):
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in SYSENT_RE.finditer(text):
            source.setdefault(match.group(1).lower(), []).append((relative, line_number(text, match.start())))

    if len(source) > 1:
        detail = "; ".join(
            f"{value}: " + ", ".join(f"{path}:{line}" for path, line in locations)
            for value, locations in sorted(source.items())
        )
        findings.append(finding(
            "CONTRADICTED", "FW 14.00 SYSENT offset", detail=detail +
            "; no firmware-matched evidence authorizes choosing a value"))

    # These are evidence inputs, not source files.  Their absence must remain visible.
    for relative in ("libSceNKWebKit.sprx.decrypted", "kernel.elf",
                     "find_webkit_gadgets_1400.py"):
        if not (root / relative).exists():
            findings.append(finding("UNVERIFIED", f"FW 14.00 evidence input {relative}", relative,
                                    detail="not included; no byte/hash/extraction check can run"))

    # Check for the provenance details the ledger requires without assuming one spelling.
    for relative in ("1400.c", "1400_offsets.txt", "webkit_gadgets_1400.js"):
        path = root / relative
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace")
            if "http://" not in text and "https://" not in text:
                findings.append(finding("UNVERIFIED", f"provenance URL for {relative}", relative,
                                        detail="file names a source but contains no URL"))

    return {
        "repository": str(root),
        "required_files": list(REQUIRED),
        "findings": findings,
    }


def render(report: dict) -> str:
    lines = ["FW14 audit report", "=================", ""]
    if not report["findings"]:
        return "\n".join(lines + ["No findings."])
    for item in report["findings"]:
        location = item["path"] or "repository"
        if item["line"]:
            location += f":{item['line']}"
        lines.append(f"[{item['status']}] {item['claim']} ({location})")
        if item["detail"]:
            lines.append(f"  {item['detail']}")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = audit(args.root.resolve())
    output = json.dumps(report, indent=2, sort_keys=True) if args.json else render(report)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
