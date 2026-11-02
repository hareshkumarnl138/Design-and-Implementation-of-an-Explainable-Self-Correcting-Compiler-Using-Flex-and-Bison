"""Flask API and same-origin browser UI for diagnosis and validated repair."""
from pathlib import Path
import sys

from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from diagnosis.diagnose import diagnose
from diagnosis.repair import repair_source, validate_source

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
    findings = [item.to_dict() for item in diagnose(source)]
    compiler_result = validate_source(source)
    return jsonify({
        "ok": compiler_result["valid"] if compiler_result["available"] else
              not any(item["severity"] == "error" for item in findings),
        "count": len(findings),
        "findings": findings,
        "compiler_validation": compiler_result,
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
        note = "No supported repair was generated. The source was checked by the compiler."

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
