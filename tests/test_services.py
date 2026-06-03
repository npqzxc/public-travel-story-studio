import tempfile
import unittest
from pathlib import Path

from app import config, database
from app.services.dashboard_service import dashboard_api_payload
from app.services.ticket_service import ticket_api_detail, ticket_api_list


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "ops.sqlite3"
        self.original_db_path = config.SETTINGS.db_path
        config.SETTINGS.__dict__["db_path"] = self.db_path
        database.init_db(self.db_path)

    def tearDown(self):
        config.SETTINGS.__dict__["db_path"] = self.original_db_path
        self.temp_dir.cleanup()

    def test_dashboard_payload_contains_spotlights(self):
        payload = dashboard_api_payload()
        self.assertIn("spotlights", payload)
        self.assertTrue(payload["spotlights"])

    def test_ticket_api_endpoints_return_structured_data(self):
        collection = ticket_api_list({"status": "blocked"})
        self.assertEqual(collection["filters"]["status"], "blocked")
        self.assertGreaterEqual(collection["meta"]["count"], 1)

        detail = ticket_api_detail(1)
        self.assertIsNotNone(detail)
        self.assertIn("comments", detail)


if __name__ == "__main__":
    unittest.main()
