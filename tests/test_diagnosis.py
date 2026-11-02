import unittest

from backend.app import app
from diagnosis.diagnose import diagnose
from diagnosis.repair import repair_source, validate_source


class DiagnosisTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_unmatched_open_brace(self):
        self.assertTrue(any(f.code == "SYN002" for f in diagnose("int main() {\\n return 0;\\n")))

    def test_unmatched_closing_brace(self):
        self.assertTrue(any(f.code == "SYN001" for f in diagnose("int main() { return 0; }}")))

    def test_possible_missing_semicolon(self):
        self.assertTrue(any(f.code == "SYN003" for f in diagnose("int main() {\\n int x = 5\\n return x;\\n}")))

    def test_ignores_delimiters_in_strings_comments(self):
        findings = diagnose('int main() { printf("}"); /* ( ] */ return 0; }')
        self.assertFalse(any(f.code in {"SYN001", "SYN002"} for f in findings))

    def test_generates_simple_semicolon_candidate(self):
        fixed, repairs = repair_source("int main() {\\n return 0\\n}\\n")
        self.assertIn("return 0;", fixed)
        self.assertEqual(len(repairs), 1)

    def test_control_header_not_repaired(self):
        source = "if (x == 1)\\n"
        self.assertEqual(repair_source(source), (source, []))

    def test_compiler_accepts_valid_source(self):
        result = validate_source("int main(void) { return 0; }")
        self.assertTrue(result["available"], result["stderr"])
        self.assertTrue(result["valid"], result["stderr"])

    def test_api_applies_only_compiler_validated_repair(self):
        response = self.client.post(
            "/api/repair",
            json={"source": "int main(void) {\\n return 0\\n}\\n"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["changed"])
        self.assertTrue(data["validation"]["valid"])
        self.assertIn("return 0;", data["source"])

    def test_api_rejects_repair_with_semantic_error(self):
        source = "int main(void) {\\n missing = 5\\n return 0;\\n}\\n"
        response = self.client.post("/api/repair", json={"source": source})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data["changed"])
        self.assertTrue(data["candidate_rejected"])
        self.assertEqual(data["source"], source)
        self.assertFalse(data["validation"]["valid"])

    def test_api_rejects_non_json_payload(self):
        response = self.client.post("/api/repair", data="not json", content_type="text/plain")
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
