"""Flask API and same-origin browser UI for diagnosis and validated repair."""
from pathlib import Path
import re
import sys

from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from diagnosis.diagnose import diagnose
from diagnosis.repair import repair_source, validate_source
from diagnosis.semantic_hints import compiler_findings

app = Flask(__name__)
MAX_SOURCE_CHARS = 100_000


def read_source():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return None, (jsonify({"error": "Expected a JSON object with a 'source' string."}), 400)
    source = payload.get("source")
    if not isinstance(source, str):
        return None, (jsonify({"error": "'source' must be a string."}), 400)
    if len(source) > MAX_SOURCE_CHARS:
        return None, (jsonify({"error": "Source exceeds 100000 characters."}), 413)
    return source, None


@app.get("/")
def index():
    return send_from_directory(ROOT / "frontend", "index.html")


@app.get("/api/health")
def health():
    compiler = validate_source("")
    return jsonify({
        "status": "ok",
        "service": "smartfix-compiler-api",
        "compiler_available": compiler["available"],
    })


@app.post("/api/diagnose")
def api_diagnose():
    source, error = read_source()
    if error:
        return error
    compiler_result = validate_source(source)
    findings = [item.to_dict() for item in diagnose(source)]
    if compiler_result["available"]:
        findings.extend(item.to_dict() for item in compiler_findings(source, compiler_result["stderr"]))
    return jsonify({
        "ok": compiler_result["valid"] if compiler_result["available"] else
              not any(item["severity"] == "error" for item in findings),
        "count": len(findings),
        "findings": findings,
        "compiler_validation": compiler_result,
    })


@app.post("/api/repair/confirm")
def api_confirm_semantic_repair():
    """Apply a user-selected spelling candidate only after compiler validation."""
    source, error = read_source()
    if error:
        return error
    payload = request.get_json(silent=True) or {}
    line = payload.get("line")
    column = payload.get("column")
    identifier = payload.get("identifier")
    replacement = payload.get("replacement")
    if (not isinstance(line, int) or not isinstance(column, int)
            or not isinstance(identifier, str) or not isinstance(replacement, str)):
        return jsonify({"error": "line, column, identifier and replacement are required."}), 400

    initial = validate_source(source)
    if not initial["available"]:
        return jsonify({"changed": False, "source": source, "note": initial["stderr"]}), 503
    semantic = compiler_findings(source, initial["stderr"])
    finding = next((item for item in semantic
                    if item.code == "SEM002" and item.line == line
                    and item.column == column
                    and item.message == f"Undeclared identifier '{identifier}'."), None)
    if finding is None or replacement not in finding.candidates:
        return jsonify({"error": "The selected candidate is not valid for this diagnostic."}), 400

    source_lines = source.splitlines(keepends=True)
    if line < 1 or line > len(source_lines):
        return jsonify({"error": "Diagnostic line is outside the source."}), 400
    line_text = source_lines[line - 1]
    start = column - 1
    token = re.compile(r"[A-Za-z_]\w*").match(line_text, start)
    if token is None or token.group(0) != identifier:
        return jsonify({"error": "The identifier no longer matches the diagnostic location."}), 409
    source_lines[line - 1] = line_text[:start] + replacement + line_text[token.end():]
    candidate = "".join(source_lines)
    validation = validate_source(candidate)
    if not validation["available"] or not validation["valid"]:
        return jsonify({
            "changed": False, "source": source, "validation": validation,
            "note": "The selected correction did not pass compiler validation. Original source preserved."
        })
    return jsonify({
        "changed": True, "source": candidate, "validation": validation,
        "note": f"Replaced '{identifier}' with '{replacement}'. The selected correction passed compiler validation."
    })


@app.post("/api/repair")
def api_repair():
    source, error = read_source()
    if error:
        return error

    candidate, repairs = repair_source(source)
    validation = validate_source(candidate)
    accepted = candidate != source and bool(repairs) and validation["available"] and validation["valid"]
    corrected = candidate if accepted else source
    findings = [item.to_dict() for item in diagnose(corrected)]
    if validation["available"]:
        findings.extend(item.to_dict() for item in compiler_findings(corrected, validation["stderr"]))

    if candidate != source and not accepted:
        note = (
            "The proposed edit was rejected because the compiler did not validate it. "
            "The original source was preserved."
        )
    elif accepted:
        note = "The proposed repair passed lexical, syntax, and initial semantic validation."
    elif not validation["available"]:
        note = "Compiler validation is unavailable. No automatic edit was applied."
    else:
        semantic_errors = [item for item in findings if item["code"] in {"SEM001", "SEM002"}]
        duplicate_error = next((item for item in semantic_errors if item["code"] == "SEM001"), None)
        undeclared_error = next((item for item in semantic_errors if item["code"] == "SEM002"), None)
        if duplicate_error:
            note = "A duplicate declaration was detected. " + duplicate_error["suggestion"]
        elif undeclared_error:
            note = (
                "An undeclared identifier remains. "
                + undeclared_error["suggestion"]
                + " The original source was preserved."
            )
        else:
            note = "No safe supported repair was generated. The source was checked by the compiler."

    return jsonify({
        "source": corrected,
        "changed": accepted,
        "repairs": [item.to_dict() for item in repairs] if accepted else [],
        "candidate_rejected": candidate != source and not accepted,
        "findings_after_repair": findings,
        "validation": validation,
        "note": note + " Review all changes before using the code.",
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
