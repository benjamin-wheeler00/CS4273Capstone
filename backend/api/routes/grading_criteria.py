"""Read and edit master grading criteria without changing recorded grades."""

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Lock

from flask import Blueprint, current_app, jsonify, request


# Keep these endpoints independent of transcription and AI model initialization.
grading_criteria_bp = Blueprint("grading_criteria", __name__)
# Resolve from this file so saving works regardless of the server's working directory.
MASTER_PATH = Path(__file__).resolve().parents[2] / "data" / "nature_codes_master.json"
# Protect concurrent requests handled within this server process.
_write_lock = Lock()


@grading_criteria_bp.route("/grading-criteria/<nature_code_id>", methods=["GET"])
@grading_criteria_bp.route(
    "/grading-criteria/<nature_code_id>/<question_id>", methods=["PUT"]
)
def grading_criteria(nature_code_id, question_id=None):
    """GET lists one protocol's criteria; PUT changes one existing question's text."""
    # Validate before opening the file; malformed or blank edits must never be saved.
    payload = request.get_json(silent=True) if request.method == "PUT" else None
    if request.method == "PUT" and (
        not isinstance(payload, dict)
        or not isinstance(payload.get("text"), str)
        or not payload["text"].strip()
    ):
        return jsonify(error="Criterion text must not be empty."), 400

    try:
        # Read the latest data while holding the lock so edits in this process survive.
        with _write_lock:
            master = json.loads(MASTER_PATH.read_text(encoding="utf-8"))
            if nature_code_id not in master:
                return jsonify(error="Nature code not found."), 404

            questions = master[nature_code_id].get("grading", {}).get("questions", [])
            if request.method == "GET":
                # Return only fields used by the editor, leaving internal metadata private.
                response = jsonify([
                    {"id": str(q["Question_ID"]), "text": q.get("Question_Text", "")}
                    for q in questions if q.get("Question_ID")
                ])
                # Reopening a protocol should show changes saved by other users.
                response.headers["Cache-Control"] = "no-store"
                return response

            # Match the stable ID, including subquestion IDs such as "1a".
            question = next(
                (q for q in questions if str(q.get("Question_ID")) == question_id), None
            )
            if question is None:
                return jsonify(error="Grading criterion not found."), 404

            # Preserve all other questions, classification data, and grading metadata.
            question["Question_Text"] = payload["text"].strip()
            # Write beside the master so replacement stays on the same filesystem.
            # Replace only after the complete JSON has been written successfully.
            temp_path = None
            try:
                with NamedTemporaryFile(
                    mode="w", encoding="utf-8", dir=MASTER_PATH.parent,
                    suffix=".tmp", delete=False
                ) as output:
                    temp_path = Path(output.name)
                    json.dump(master, output, indent=2, ensure_ascii=False)
                    output.write("\n")
                    # Flush Python's buffer and ask the OS to flush the file before replacing.
                    output.flush()
                    os.fsync(output.fileno())
                # Readers see either the previous complete file or the new complete file.
                os.replace(temp_path, MASTER_PATH)
            finally:
                # A failed write or replacement must not leave a temporary file behind.
                if temp_path is not None and temp_path.exists():
                    temp_path.unlink()

            return jsonify(id=question_id, text=question["Question_Text"])
    except (OSError, ValueError):
        # Log technical details on the server and return a useful message to the editor.
        current_app.logger.exception("Unable to access grading criteria")
        return jsonify(error="Unable to load or save grading criteria. Please try again."), 500
