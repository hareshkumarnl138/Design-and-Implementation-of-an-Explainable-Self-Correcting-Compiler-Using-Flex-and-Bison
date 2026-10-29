"""Flask API and same-origin browser UI for diagnosis and conservative repair."""
from pathlib import Path
import sys
from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from diagnosis.diagnose import diagnose
from diagnosis.repair import repair_source

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
    return jsonify({"status": "ok", "service": "smartfix-compiler-api"})

@app.post("/api/diagnose")
def api_diagnose():
    source, error = read_source()
    if error:
        return error
    findings = [item.to_dict() for item in diagnose(source)]
    return jsonify({
        "ok": not any(item["severity"] == "error" for item in findings),
        "count": len(findings),
        "findings": findings,
    })

@app.post("/api/repair")
def api_repair():
    source, error = read_source()
    if error:
        return error
    corrected, repairs = repair_source(source)
    findings = [item.to_dict() for item in diagnose(corrected)]
    return jsonify({
        "source": corrected,
        "changed": corrected != source,
        "repairs": [item.to_dict() for item in repairs],
        "findings_after_repair": findings,
        "note": "Repairs are heuristic. Review the result and compile it before use.",
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
