#!/usr/bin/env python3
"""Static, non-invasive audit for the PS4 firmware 14.00 research tree.

This script checks source consistency and syntax only. It does not execute
exploit code, validate firmware offsets against a console, or claim jailbreak
functionality.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
findings: list[tuple[str, str, str]] = []  # status, check, detail


def add(status: str, check: str, detail: str) -> None:
    findings.append((status, check, detail))
    print(f"[{status}] {check}: {detail}")


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


# Expected repository components and build dependencies.
for rel in ("1400.c", "1400.h", "1400_offsets.txt",
            "webkit_gadgets_1400.js", "jordy_stage2_1400.js", "exploit.html"):
    if (ROOT / rel).is_file():
        add("PASS", f"required file {rel}", "present")
    else:
        add("FAIL", f"required file {rel}", "missing")

# Resolve quoted includes from the source directory and repository root. This is
# a dependency inventory, not a substitute for compiling with the target SDK.
include_re = re.compile(r'^\s*#\s*include\s+"([^"]+)"', re.M)
source_files = sorted(
    path for pattern in ("*.c", "*.h")
    for path in ROOT.rglob(pattern)
    if not any(part.startswith(".") or part in {"node_modules", "build", "dist"}
               for part in path.relative_to(ROOT).parts[:-1])
)
missing_includes: list[str] = []
for source in source_files:
    source_text = source.read_text(encoding="utf-8", errors="replace")
    for include in include_re.findall(source_text):
        candidates = [(source.parent / include).resolve(), (ROOT / include).resolve()]
        exists_in_repo = any(
            candidate.is_relative_to(ROOT.resolve()) and candidate.is_file()
            for candidate in candidates
        )
        if exists_in_repo:
            add("PASS", f"quoted include {source.relative_to(ROOT)} -> {include}", "resolved within repository")
        else:
            finding = f"{source.relative_to(ROOT)} -> {include}"
            missing_includes.append(finding)
            add("BLOCKED", f"quoted include {finding}",
                "not resolved within this repository; may be supplied by an external SDK or missing source tree")
if not source_files:
    add("BLOCKED", "C include inventory", "no top-level C/header files found")

# Syntax checks are meaningful, but are not exploit/runtime validation.
node = shutil.which("node")
js_files = sorted(ROOT.glob("*.js"))
if not node:
    add("BLOCKED", "JavaScript syntax", "Node.js is not installed")
elif not js_files:
    add("BLOCKED", "JavaScript syntax", "no top-level .js files found")
else:
    for path in js_files:
        proc = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
        if proc.returncode == 0:
            add("PASS", f"JavaScript syntax {path.name}", "Node.js parser accepted file")
        else:
            detail = (proc.stderr or proc.stdout).strip().replace("\n", " ")
            add("FAIL", f"JavaScript syntax {path.name}", detail[:500])

# Find contradictory SYSENT claims between the C source and verification notes.
c_src = read("1400.c")
offset_notes = read("1400_offsets.txt")
c_match = re.search(r"\.SYSENT_addr\s*=\s*(0x[0-9A-Fa-f]+)", c_src)
txt_match = re.search(r"SYSENT\s*=\s*(0x[0-9A-Fa-f]+)", offset_notes)
if c_match and txt_match:
    c_value, note_value = c_match.group(1).lower(), txt_match.group(1).lower()
    if c_value == note_value:
        add("PASS", "SYSENT consistency", f"both sources say {c_value}")
    else:
        add("FAIL", "SYSENT consistency",
            f"1400.c says {c_value}; 1400_offsets.txt says {note_value}. Do not choose either without independent evidence.")
else:
    add("UNVERIFIED", "SYSENT consistency", "could not parse SYSENT from both sources")

# The stage-two JavaScript has a separate copy of the same critical offset.
# Check it independently so a stale runtime value cannot silently disagree.
stage2 = read("jordy_stage2_1400.js")
stage2_match = re.search(r"\bSYSENT\s*:\s*(0x[0-9A-Fa-f]+)", stage2)
if c_match and stage2_match:
    c_value = c_match.group(1).lower()
    stage2_value = stage2_match.group(1).lower()
    if c_value == stage2_value:
        add("PASS", "stage-two SYSENT consistency", f"1400.c and stage two both say {c_value}")
    else:
        add("FAIL", "stage-two SYSENT consistency",
            f"1400.c says {c_value}; jordy_stage2_1400.js says {stage2_value}. Do not execute with conflicting offsets.")
else:
    add("UNVERIFIED", "stage-two SYSENT consistency",
        "could not parse SYSENT from both 1400.c and jordy_stage2_1400.js")

# Placeholder / TODO scan: report counts and a small sample, not every match.
scan_files = ["exploit.html", "jordy_stage2_1400.js", "webkit_gadgets_1400.js", "1400.c"]
patterns = re.compile(r"TODO|PLACEHOLDER|PENDING_DUMP|DEADC0DE|not yet integrated|needs to be found", re.I)
hits: list[str] = []
for rel in scan_files:
    for number, line in enumerate(read(rel).splitlines(), 1):
        if patterns.search(line):
            hits.append(f"{rel}:{number}: {line.strip()[:180]}")
if hits:
    add("UNVERIFIED", "placeholder scan", f"{len(hits)} potential placeholder/TODO marker(s) found")
else:
    add("PASS", "placeholder scan", "no known placeholder markers found in scanned files")

# Gadget confidence: the source itself labels some candidates as partial and says
# the original binary is needed. Do not claim independent byte-level validation.
gadgets = read("webkit_gadgets_1400.js")
if re.search(r"partial|not followed by clean ret|verify before use", gadgets, re.I):
    add("UNVERIFIED", "WebKit gadget evidence",
        "gadget file labels candidates as partial/unverified; binary hash and reproducible extraction evidence are still needed")
else:
    add("UNVERIFIED", "WebKit gadget evidence",
        "source comments alone cannot independently verify offsets; provide the exact binary and hash")

# The HTML / stage-two sources explicitly indicate that the chain is incomplete.
combined = read("exploit.html") + "\n" + read("jordy_stage2_1400.js")
if re.search(r"not yet integrated|returns 0|TODO: verify|needs to be found|placeholder", combined, re.I):
    add("FAIL", "end-to-end FW 14.00 chain", "source contains explicit missing primitives / placeholder values")
else:
    add("UNVERIFIED", "end-to-end FW 14.00 chain",
        "static source audit cannot prove an end-to-end chain; console testing and independent evidence are required")

passed = sum(s == "PASS" for s, _, _ in findings)
failed = sum(s == "FAIL" for s, _, _ in findings)
unverified = sum(s == "UNVERIFIED" for s, _, _ in findings)
blocked = sum(s == "BLOCKED" for s, _, _ in findings)

report = [
    "# PS4 FW 14.00 Static Audit",
    "",
    "> This is a static source audit. It does not execute exploit code and cannot establish that a jailbreak works.",
    "",
    f"- PASS: {passed}",
    f"- FAIL: {failed}",
    f"- UNVERIFIED: {unverified}",
    f"- BLOCKED: {blocked}",
    "",
    "## Findings",
    "",
]
for status, check, detail in findings:
    report.append(f"- **{status} — {check}:** {detail}")
report += [
    "",
    "## Evidence required before claiming support",
    "",
    "- Exact firmware/module identity and cryptographic hash for every binary used in gadget verification.",
    "- Reproducible byte-pattern extraction output tied to that binary; distinguish complete gadgets from partial matches.",
    "- Independent evidence for each FW 14.00 kernel offset; resolve source conflicts rather than copying values between firmware versions.",
    "- Successful tests on actual FW 14.00 hardware, with test conditions and outcomes recorded.",
    "",
]
(ROOT / "audit-report.md").write_text("\n".join(report), encoding="utf-8")
print(f"\nSummary: PASS={passed} FAIL={failed} UNVERIFIED={unverified} BLOCKED={blocked}")
print(f"Report written to {ROOT / 'audit-report.md'}")
