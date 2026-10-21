import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "audit_fw14.py"
SPEC = importlib.util.spec_from_file_location("audit_fw14", SCRIPT)
audit_fw14 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(audit_fw14)


class AuditFw14Tests(unittest.TestCase):
    def test_real_checkout_reports_sysent_contradiction_and_missing_inputs(self):
        report = audit_fw14.audit(SCRIPT.parents[1])
        statuses = {(item["status"], item["claim"]) for item in report["findings"]}
        self.assertIn(("CONTRADICTED", "FW 14.00 SYSENT offset"), statuses)
        self.assertIn(("UNVERIFIED", "FW 14.00 evidence input kernel.elf"), statuses)

    def test_clean_fixture_has_no_false_positive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in audit_fw14.REQUIRED:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("SYSENT = 0x1102b70\nhttps://example.invalid/source\n", encoding="utf-8")
            for relative in ("sections.h", "offsets.h", "offsets/1400.h",
                             "libSceNKWebKit.sprx.decrypted", "kernel.elf",
                             "find_webkit_gadgets_1400.py"):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"fixture")
            report = audit_fw14.audit(root)
            self.assertEqual([], report["findings"])

    def test_alternate_sysent_spelling_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in audit_fw14.REQUIRED:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                value = "SYSENT_addr: 0x1102b70" if relative == "1400.c" else "SYSENT = 0x110a760"
                path.write_text(value + "\nhttps://example.invalid/source\n", encoding="utf-8")
            for relative in ("sections.h", "offsets.h", "offsets/1400.h",
                             "libSceNKWebKit.sprx.decrypted", "kernel.elf",
                             "find_webkit_gadgets_1400.py"):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"fixture")
            claims = audit_fw14.audit(root)["findings"]
            self.assertTrue(any(item["status"] == "CONTRADICTED" for item in claims))


if __name__ == "__main__":
    unittest.main()
