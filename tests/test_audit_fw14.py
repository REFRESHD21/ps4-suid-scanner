"""Smoke tests for the FW14 static audit using isolated temporary trees."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT = REPO / "tools" / "audit_fw14.py"


class AuditSmokeTests(unittest.TestCase):
    def make_tree(self, *, c_sysent: str, note_sysent: str, stage2: str = "var K = { SYSENT: 0x01102B70 }; function example() { return 0; }") -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / "tools").mkdir()
        shutil.copy2(AUDIT_SCRIPT, root / "tools" / "audit_fw14.py")

        files = {
            "1400.c": f"struct offsets {{ unsigned long SYSENT_addr; }};\nstruct offsets offsets = {{ .SYSENT_addr = {c_sysent} }};\n",
            "1400.h": "/* fixture */\n",
            "1400_offsets.txt": f"// SYSENT = {note_sysent}\n",
            "webkit_gadgets_1400.js": "const candidate = 1;\n",
            "jordy_stage2_1400.js": stage2 + "\n",
            "exploit.html": "<!doctype html><title>audit fixture</title>\n",
        }
        for rel, data in files.items():
            (root / rel).write_text(data, encoding="utf-8")
        return root

    def run_audit(self, root: Path) -> str:
        proc = subprocess.run(
            [sys.executable, str(root / "tools" / "audit_fw14.py")],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)
        report = root / "audit-report.md"
        self.assertTrue(report.is_file(), "audit report should be generated")
        return report.read_text(encoding="utf-8")

    def test_conflicting_sysent_is_reported(self) -> None:
        root = self.make_tree(c_sysent="0x01102B70", note_sysent="0x0110A760")
        report = self.run_audit(root)
        self.assertIn("FAIL — SYSENT consistency", report)
        self.assertIn("0x01102b70", report)
        self.assertIn("0x0110a760", report)

    def test_ordinary_return_zero_is_not_a_placeholder(self) -> None:
        root = self.make_tree(c_sysent="0x01102B70", note_sysent="0x01102B70")
        report = self.run_audit(root)
        self.assertIn("PASS — placeholder scan", report)
        self.assertIn("PASS — SYSENT consistency", report)
        self.assertIn("UNVERIFIED — end-to-end FW 14.00 chain", report)

    def test_stage2_sysent_mismatch_is_reported(self) -> None:
        root = self.make_tree(
            c_sysent="0x01102B70",
            note_sysent="0x01102B70",
            stage2="var K = { SYSENT: 0x0110A760 };",
        )
        report = self.run_audit(root)
        self.assertIn("FAIL — stage-two SYSENT consistency", report)
        self.assertIn("0x01102b70", report)
        self.assertIn("0x0110a760", report)

    def test_missing_quoted_c_include_is_reported_as_blocked(self) -> None:
        root = self.make_tree(c_sysent="0x01102B70", note_sysent="0x01102B70")
        source = root / "1400.c"
        source.write_text('#include "missing_dependency.h"\\n' + source.read_text(encoding="utf-8"), encoding="utf-8")
        report = self.run_audit(root)
        self.assertIn("BLOCKED — quoted include 1400.c -> missing_dependency.h", report)

    def test_nested_c_header_includes_are_scanned(self) -> None:
        root = self.make_tree(c_sysent="0x01102B70", note_sysent="0x01102B70")
        nested = root / "src" / "include"
        nested.mkdir(parents=True)
        (nested / "nested.h").write_text('#include "missing_nested.h"\\n', encoding="utf-8")
        report = self.run_audit(root)
        self.assertIn("BLOCKED — quoted include src/include/nested.h -> missing_nested.h", report)

    def test_partial_gadget_claim_remains_unverified(self) -> None:
        root = self.make_tree(c_sysent="0x01102B70", note_sysent="0x01102B70")
        (root / "webkit_gadgets_1400.js").write_text(
            "// partial match; verify before use\nconst candidate = 1;\n",
            encoding="utf-8",
        )
        report = self.run_audit(root)
        self.assertIn("UNVERIFIED — WebKit gadget evidence", report)
        self.assertIn("binary hash and reproducible extraction evidence are still needed", report)

    def test_blanket_verified_claim_conflicts_with_partial_gadget(self) -> None:
        root = self.make_tree(
            c_sysent="0x01102B70",
            note_sysent="0x01102B70",
            stage2='log("WebKit gadgets: 17/17 verified");',
        )
        (root / "webkit_gadgets_1400.js").write_text(
            "// partial: not followed by clean ret\\nconst candidate = 1;\\n",
            encoding="utf-8",
        )
        report = self.run_audit(root)
        self.assertIn("FAIL — contradictory gadget confidence claim", report)
        self.assertIn("repository claims 17/17 gadgets verified", report)



    def test_unsupported_webkit_identity_claim_is_reported(self) -> None:
        root = self.make_tree(c_sysent="0x01102B70", note_sysent="0x01102B70")
        (root / "webkit_gadgets_1400.js").write_text(
            "// All offsets confirmed identical to 13.04 (WebKit not updated in 14.00)\\n",
            encoding="utf-8",
        )
        report = self.run_audit(root)
        self.assertIn("FAIL — unsupported WebKit identity claim", report)
        self.assertIn("without matching-binary evidence", report)

    def test_strict_mode_succeeds_when_no_fail_findings_exist(self) -> None:
        root = self.make_tree(
            c_sysent="0x01102B70",
            note_sysent="0x01102B70",
            stage2="var K = { SYSENT: 0x01102B70 }; function example() { return 0; }",
        )
        proc = subprocess.run(
            [sys.executable, str(root / "tools" / "audit_fw14.py"), "--strict"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)
        self.assertIn("Summary:", proc.stdout)

    def test_strict_mode_fails_on_audit_contradictions(self) -> None:
        root = self.make_tree(
            c_sysent="0x01102B70",
            note_sysent="0x0110A760",
        )
        proc = subprocess.run(
            [sys.executable, str(root / "tools" / "audit_fw14.py"), "--strict"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)
        self.assertIn("Strict mode: failing because", proc.stderr)

    def test_readme_blanket_verified_claim_conflicts_with_partial_gadget(self) -> None:
        root = self.make_tree(c_sysent="0x01102B70", note_sysent="0x01102B70")
        (root / "README.md").write_text(
            "WebKit gadgets: 17/17 verified\\n",
            encoding="utf-8",
        )
        (root / "webkit_gadgets_1400.js").write_text(
            "// partial: not followed by clean ret\\nconst candidate = 1;\\n",
            encoding="utf-8",
        )
        report = self.run_audit(root)
        self.assertIn("FAIL — contradictory gadget confidence claim", report)
        self.assertIn("repository claims 17/17 gadgets verified", report)



if __name__ == "__main__":
    unittest.main()
