import unittest

from backend.app import app
from diagnosis.diagnose import diagnose
from diagnosis.repair import repair_source, validate_source
from diagnosis.semantic_hints import compiler_findings


class DiagnosisTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_unmatched_open_brace(self):
        self.assertTrue(any(f.code == "SYN002" for f in diagnose("int main() {\n return 0;\n")))

    def test_unmatched_closing_brace(self):
        self.assertTrue(any(f.code == "SYN001" for f in diagnose("int main() { return 0; }}")))

    def test_possible_missing_semicolon(self):
        self.assertTrue(any(f.code == "SYN003" for f in diagnose("int main() {\n int x = 5\n return x;\n}")))

    def test_ignores_delimiters_in_strings_comments(self):
        findings = diagnose('int main() { printf("}"); /* ( ] */ return 0; }')
        self.assertFalse(any(f.code in {"SYN001", "SYN002"} for f in findings))

    def test_generates_simple_semicolon_candidate(self):
        fixed, repairs = repair_source("int main() {\n return 0\n}\n")
        self.assertIn("return 0;", fixed)
        self.assertEqual(len(repairs), 1)

    def test_generates_missing_closing_brace_candidate(self):
        source = "int main() {\n int a = 10;\n return a;\n"
        fixed, repairs = repair_source(source)
        self.assertTrue(fixed.rstrip().endswith("}"))
        self.assertEqual([repair.rule for repair in repairs], ["FIX002"])

    def test_api_applies_compiler_validated_closing_brace_repair(self):
        source = "int main() {\n int a = 10;\n return a;\n"
        response = self.client.post("/api/repair", json={"source": source})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["changed"], data["validation"]["stderr"])
        self.assertTrue(data["validation"]["valid"])
        self.assertTrue(data["source"].rstrip().endswith("}"))
        self.assertEqual(data["repairs"][0]["rule"], "FIX002")

    def test_control_header_not_repaired(self):
        source = "if (x == 1)\n"
        self.assertEqual(repair_source(source), (source, []))

    def test_compiler_accepts_valid_source(self):
        result = validate_source("int main(void) { return 0; }")
        self.assertTrue(result["available"], result["stderr"])
        self.assertTrue(result["valid"], result["stderr"])

    def test_api_applies_only_compiler_validated_repair(self):
        response = self.client.post(
            "/api/repair",
            json={"source": "int main(void) {\n return 0\n}\n"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["changed"])
        self.assertTrue(data["validation"]["valid"])
        self.assertIn("return 0;", data["source"])

    def test_api_rejects_repair_with_semantic_error(self):
        source = "int main(void) {\n missing = 5\n return 0;\n}\n"
        response = self.client.post("/api/repair", json={"source": source})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data["changed"])
        self.assertTrue(data["candidate_rejected"])
        self.assertEqual(data["source"], source)
        self.assertFalse(data["validation"]["valid"])

    def test_repair_proposes_unique_undeclared_identifier_typo(self):
        source = "int main(void) { int total = 1; return totla; }"
        candidate, repairs = repair_source(source)
        self.assertIn("return total;", candidate)
        self.assertEqual([repair.rule for repair in repairs], ["FIX003"])

    def test_duplicate_declaration_is_not_automatically_changed(self):
        source = "int main(void) { int value = 1; int value = 2; return value; }"
        candidate, repairs = repair_source(source)
        self.assertEqual(candidate, source)
        self.assertEqual(repairs, [])

    def test_undeclared_identifier_suggests_close_declared_name(self):
        findings = compiler_findings(
            "int main(void) { int total = 1; return totla; }",
            "-:1:42: error[SEM002]: Use of undeclared identifier 'totla'",
        )
        self.assertEqual(findings[0].code, "SEM002")
        self.assertIn("total", findings[0].suggestion)

    def test_ambiguous_typo_does_not_guess_between_equal_candidates(self):
        findings = compiler_findings(
            "int main(void) { int cat = 1; int car = 2; return cap; }",
            "-:1:55: error[SEM002]: Use of undeclared identifier 'cap'",
        )
        self.assertEqual(findings[0].code, "SEM002")
        self.assertIn("equally close", findings[0].suggestion)
        self.assertNotIn("Did you mean", findings[0].suggestion)

    def test_ambiguous_candidates_are_exposed_for_user_selection(self):
        findings = compiler_findings(
            "int main(void) { int cat = 1; int car = 2; return cap; }",
            "-:1:55: error[SEM002]: Use of undeclared identifier 'cap'",
        )
        self.assertEqual(set(findings[0].candidates), {"cat", "car"})

    def test_api_applies_user_selected_ambiguous_typo_after_validation(self):
        source = (
            "int main(void) {\n"
            "    int cat = 1;\n"
            "    int car = 2;\n"
            "    return cap;\n"
            "}\n"
        )
        response = self.client.post("/api/repair/confirm", json={
            "source": source, "line": 4, "column": 12,
            "identifier": "cap", "replacement": "cat",
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["changed"], data.get("validation"))
        self.assertTrue(data["validation"]["valid"])
        self.assertIn("return cat;", data["source"])

    def test_api_rejects_unoffered_semantic_candidate(self):
        source = "int main(void) { int cat = 1; int car = 2; return cap; }"
        response = self.client.post("/api/repair/confirm", json={
            "source": source, "line": 1, "column": 55,
            "identifier": "cap", "replacement": "dog",
        })
        self.assertEqual(response.status_code, 400)

    def test_duplicate_declaration_explains_manual_choices(self):
        findings = compiler_findings(
            "int main(void) { int value = 1; int value = 2; return value; }",
            "-:1:39: error[SEM001]: Redeclaration of 'value' in the same scope",
        )
        self.assertEqual(findings[0].code, "SEM001")
        self.assertIn("Rename one declaration", findings[0].suggestion)

    def test_api_validates_and_applies_unique_typo_repair(self):
        source = "int main(void) { int total = 1; return totla; }"
        response = self.client.post("/api/repair", json={"source": source})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["changed"], data["validation"]["stderr"])
        self.assertTrue(data["validation"]["valid"])
        self.assertIn("return total;", data["source"])
        self.assertEqual(data["repairs"][0]["rule"], "FIX003")

    def test_api_keeps_duplicate_declaration_for_manual_decision(self):
        source = "int main(void) { int value = 1; int value = 2; return value; }"
        response = self.client.post("/api/repair", json={"source": source})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data["changed"])
        self.assertEqual(data["source"], source)
        self.assertIn("duplicate declaration", data["note"].lower())
        self.assertTrue(any(f["code"] == "SEM001" for f in data["findings_after_repair"]))

    def test_api_repair_note_explains_ambiguous_typo_without_guessing(self):
        source = (
            "int main(void) {\n"
            "    int cat = 1;\n"
            "    int car = 2;\n"
            "    return cap;\n"
            "}\n"
        )
        response = self.client.post("/api/repair", json={"source": source})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data["changed"])
        self.assertIn("equally close", data["note"])
        self.assertTrue(any(
            item["code"] == "SEM002"
            and "equally close" in item["suggestion"]
            for item in data["findings_after_repair"]
        ))

    def test_api_includes_compiler_semantic_hints(self):
        response = self.client.post("/api/diagnose", json={
            "source": "int main(void) { int total = 1; return totla; }"
        })
        self.assertEqual(response.status_code, 200)
        findings = response.get_json()["findings"]
        semantic = [item for item in findings if item["code"] == "SEM002"]
        self.assertTrue(semantic)
        self.assertIn("total", semantic[0]["suggestion"])

    def test_api_rejects_non_json_payload(self):
        response = self.client.post("/api/repair", data="not json", content_type="text/plain")
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
