"""Exercise criterion edits against a temporary copy of the master data."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from flask import Flask

from api.routes import grading_criteria as routes


class GradingCriteriaTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "nature_codes_master.json"
        self.original = json.loads(routes.MASTER_PATH.read_text(encoding="utf-8"))
        self.path.write_text(json.dumps(self.original), encoding="utf-8")
        patcher = patch.object(routes, "MASTER_PATH", self.path)
        patcher.start()
        self.addCleanup(patcher.stop)
        app = Flask(__name__)
        app.register_blueprint(routes.grading_criteria_bp, url_prefix="/api")
        self.client = app.test_client()

    def test_reads_exact_protocol_questions(self):
        for code in ("0", "1"):
            response = self.client.get(f"/api/grading-criteria/{code}")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [
                {"id": str(q["Question_ID"]), "text": q.get("Question_Text", "")}
                for q in self.original[code]["grading"]["questions"] if q.get("Question_ID")
            ])

    def test_edit_persists_only_target_text_and_survives_reload(self):
        expected = copy.deepcopy(self.original)
        # Include Case Entry's subquestions and an independent nature code.
        for code, index, text in (("0", 1, "Confirm location — café?"), ("1", 0, "Check alertness?")):
            question = expected[code]["grading"]["questions"][index]
            response = self.client.put(
                f"/api/grading-criteria/{code}/{question['Question_ID']}",
                json={"text": f"  {text}  "},
            )
            self.assertEqual(response.status_code, 200)
            question["Question_Text"] = text
            loaded = self.client.get(f"/api/grading-criteria/{code}").json
            self.assertEqual(loaded[index]["text"], text)
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), expected)

    def test_invalid_edits_do_not_write(self):
        before = self.path.read_bytes()
        for payload in ({}, {"text": " \n "}, {"text": None}, {"text": 12}, [], "text"):
            response = self.client.put("/api/grading-criteria/0/1", json=payload)
            self.assertEqual(response.status_code, 400)
        for path in ("unknown/1", "0/unknown"):
            response = self.client.put(f"/api/grading-criteria/{path}", json={"text": "Changed"})
            self.assertEqual(response.status_code, 404)
        self.assertEqual(self.path.read_bytes(), before)

    def test_failed_replace_preserves_file_and_cleans_temp_file(self):
        before = self.path.read_bytes()
        with patch.object(routes.os, "replace", side_effect=OSError("Write failed")):
            response = self.client.put("/api/grading-criteria/0/1", json={"text": "Changed"})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])


if __name__ == "__main__":
    unittest.main()
