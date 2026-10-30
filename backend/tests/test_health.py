import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


class HealthRouteTest(unittest.TestCase):
    def test_health_route_returns_ok_without_model_initialization(self):
        from api import app as app_module

        with patch.dict(os.environ, {"DOCKER_CONTAINER": "true"}), patch.object(
            app_module, "check_ollama_ready", return_value=False
        ):
            create_app = app_module.create_app
            client = create_app().test_client()
            response = client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
