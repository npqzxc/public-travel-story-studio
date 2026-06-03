import tempfile
import unittest
from pathlib import Path

from app.database import (
    add_comment,
    authenticate_user,
    create_ticket,
    get_ticket,
    init_db,
    list_tickets,
    update_ticket_status,
)


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "ops.sqlite3"
        init_db(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_seeded_authentication_works(self):
        user = authenticate_user("yuki", "travel123", self.db_path)
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "yuki")

    def test_ticket_filters_and_mutations(self):
        blocked = list_tickets({"status": "blocked"}, self.db_path)
        self.assertTrue(blocked)
        self.assertTrue(all(item["status"] == "blocked" for item in blocked))

        ticket_id = create_ticket(
            project_id=1,
            title="Need a regression checklist",
            description="Support asked for a pre-release regression checklist before the alert rewrite lands.",
            priority="medium",
            assignee_id=2,
            due_date="2026-06-03",
            reporter_id=1,
            db_path=self.db_path,
        )
        add_comment(ticket_id, 1, "Started a draft in the release notes section.", self.db_path)
        update_ticket_status(ticket_id, 1, "review", self.db_path)

        created = get_ticket(ticket_id, self.db_path)
        self.assertEqual(created["status"], "review")
        self.assertEqual(len(created["comments"]), 1)
        self.assertEqual(created["comments"][0]["author_username"], "yuki")


if __name__ == "__main__":
    unittest.main()
