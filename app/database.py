from __future__ import annotations

import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from .auth import hash_password
from .config import SETTINGS

STATUS_OPTIONS = ("todo", "in_progress", "blocked", "review", "done")
PRIORITY_OPTIONS = ("low", "medium", "high", "urgent")


def _timestamp() -> str:
    return sqlite3.Timestamp.fromisoformat("2026-05-25 09:00:00").isoformat(sep=" ")


def _now() -> str:
    return sqlite3.Timestamp.now().isoformat(sep=" ", timespec="seconds")


def connect(db_path: str | Path | None = None) -> sqlite3.Connection:
    resolved = Path(db_path or SETTINGS.db_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(resolved)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str | Path | None = None) -> None:
    with connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                role TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                summary TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES projects(id),
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                reporter_id INTEGER NOT NULL REFERENCES users(id),
                assignee_id INTEGER NOT NULL REFERENCES users(id),
                due_date TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
                author_id INTEGER NOT NULL REFERENCES users(id),
                body TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ticket_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
                actor_id INTEGER NOT NULL REFERENCES users(id),
                event_type TEXT NOT NULL,
                details TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )

        user_count = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
        if user_count == 0:
            _seed(conn)


def _seed(conn: sqlite3.Connection) -> None:
    password_hash = hash_password("travel123")
    users = [
        ("yuki", "Ana Gomez", "ops_lead"),
        ("mika", "Mika Chen", "staff_engineer"),
        ("liam", "Liam Park", "product_myukiger"),
        ("sara", "Sara Ibrahim", "qa_lead"),
        ("omar", "Omar Singh", "support_engineer"),
    ]
    conn.executemany(
        "INSERT INTO users (username, display_name, role, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
        [(username, display_name, role, password_hash, _timestamp()) for username, display_name, role in users],
    )

    projects = [
        ("ORBIT", "Orbit Billing", "Modernize billing alerts and invoice reconciliation.", "active"),
        ("PULSE", "Pulse Status", "Internal reliability console for support operations.", "active"),
        ("QUARTZ", "Quartz Insights", "Analytics workbench for executive reporting.", "active"),
    ]
    conn.executemany(
        "INSERT INTO projects (code, name, summary, status, created_at) VALUES (?, ?, ?, ?, ?)",
        [(code, name, summary, status, _timestamp()) for code, name, summary, status in projects],
    )

    tickets = [
        (1, "Alert summaries ignore invoice retries", "Status digest currently omits retry attempts created after midnight, so support misses slow-burn payment failures.", "in_progress", "high", 1, 2, "2026-05-28", "2026-05-20 09:00:00", "2026-05-24 16:20:00"),
        (1, "Backfill export takes over 10 minutes", "Finance wants the CSV export to stay under three minutes even when a week of invoices needs replaying.", "blocked", "urgent", 3, 1, "2026-05-26", "2026-05-18 11:00:00", "2026-05-24 09:45:00"),
        (2, "Incident timeline needs richer ownership", "Support engineers cannot tell who took over an escalation when the timeline only shows the current assignee.", "todo", "medium", 5, 4, "2026-06-02", "2026-05-21 14:00:00", "2026-05-21 14:00:00"),
        (2, "Status page dark-launch checklist", "Prepare the release checklist and add missing verification tasks before enabling the new header layout.", "review", "medium", 4, 3, "2026-05-30", "2026-05-17 10:10:00", "2026-05-23 17:10:00"),
        (3, "Quarterly metrics missing support tag", "Executive report excludes tickets labeled as support-originated, which understates maintenance work.", "done", "low", 2, 5, "2026-05-22", "2026-05-10 08:00:00", "2026-05-22 12:00:00"),
        (3, "Refresh dashboard copy for audit review", "Audit reviewers asked for clearer language around freshness guarantees and delayed sync warnings.", "todo", "low", 3, 2, "2026-06-05", "2026-05-25 08:30:00", "2026-05-25 08:30:00"),
        (1, "Manual retry button needs safer copy", "The billing team wants more explicit warning text before replaying alerts against historical jobs.", "in_progress", "medium", 1, 5, "2026-05-29", "2026-05-22 13:15:00", "2026-05-24 18:40:00"),
        (2, "Export timeline as JSON for audit bot", "Compliance automation needs a JSON feed that mirrors the timeline UI for incident review sampling.", "review", "high", 4, 2, "2026-05-31", "2026-05-19 09:20:00", "2026-05-24 11:10:00"),
    ]
    conn.executemany(
        """
        INSERT INTO tickets (
            project_id, title, description, status, priority, reporter_id, assignee_id,
            due_date, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        tickets,
    )

    comments = [
        (1, 2, "I traced the missing retries to an old daily snapshot query. The UI can stay the same if we widen that aggregation window.", "2026-05-23 10:30:00"),
        (1, 1, "Please keep the digest readable for support. We need counts plus the top three affected accounts.", "2026-05-24 09:12:00"),
        (2, 1, "Blocked on a production-safe replay fixture. Once we have a scrubbed dataset I can benchmark this properly.", "2026-05-24 09:46:00"),
        (3, 4, "A handoff trail should include both previous and next owner. Support escalations bounce between two rotations.", "2026-05-22 16:10:00"),
        (4, 3, "Checklist draft is ready. I still need QA sign-off on the smoke test section.", "2026-05-23 17:11:00"),
        (5, 5, "Tag mapping was fixed in the ETL job. We should still backfill the last two weekly reports.", "2026-05-22 12:01:00"),
        (7, 5, "We also need a sentence explaining that manual retries may duplicate downstream notifications.", "2026-05-24 18:41:00"),
        (8, 2, "The audit bot only needs read-only fields, so this can reuse most of the list query output.", "2026-05-24 11:11:00"),
    ]
    conn.executemany(
        "INSERT INTO comments (ticket_id, author_id, body, created_at) VALUES (?, ?, ?, ?)",
        comments,
    )

    events = [
        (1, 1, "created", "Ana opened the issue after support noticed silent payment retries.", "2026-05-20 09:00:00"),
        (1, 2, "status", "Moved ticket into active investigation.", "2026-05-21 10:00:00"),
        (2, 3, "created", "Finance raised the export regression during monthly close.", "2026-05-18 11:00:00"),
        (2, 1, "status", "Marked as blocked until sanitized replay data is available.", "2026-05-24 09:45:00"),
        (3, 5, "created", "Support requested ownership history before next escalation review.", "2026-05-21 14:00:00"),
        (4, 4, "created", "QA opened a release-readiness checklist task.", "2026-05-17 10:10:00"),
        (4, 3, "status", "Moved into review after PM checklist pass.", "2026-05-23 17:10:00"),
        (5, 2, "created", "Analytics bug filed during quarterly report sign-off.", "2026-05-10 08:00:00"),
        (5, 5, "status", "Closed after ETL patch and report backfill.", "2026-05-22 12:00:00"),
        (6, 3, "created", "Copy review requested ahead of audit walkthrough.", "2026-05-25 08:30:00"),
        (7, 1, "created", "Support asked for safer language on the retry workflow.", "2026-05-22 13:15:00"),
        (8, 4, "created", "Compliance requested an audit-exportable incident timeline.", "2026-05-19 09:20:00"),
        (8, 2, "status", "Moved to review while API payload shape is validated.", "2026-05-24 11:10:00"),
    ]
    conn.executemany(
        "INSERT INTO ticket_events (ticket_id, actor_id, event_type, details, created_at) VALUES (?, ?, ?, ?, ?)",
        events,
    )

    conn.commit()


def list_team_members(db_path: str | Path | None = None) -> list[dict[str, Any]]:
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id, username, display_name, role FROM users ORDER BY display_name"
        ).fetchall()
    return [dict(row) for row in rows]


def list_projects(db_path: str | Path | None = None) -> list[dict[str, Any]]:
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id, code, name, summary, status FROM projects ORDER BY name"
        ).fetchall()
    return [dict(row) for row in rows]


def authenticate_user(username: str, password: str, db_path: str | Path | None = None) -> dict[str, Any] | None:
    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, username, display_name, role, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    if row is None or row["password_hash"] != hash_password(password):
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "display_name": row["display_name"],
        "role": row["role"],
    }


def get_user(user_id: int, db_path: str | Path | None = None) -> dict[str, Any] | None:
    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, username, display_name, role FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def dashboard_summary(db_path: str | Path | None = None) -> dict[str, Any]:
    tickets = list_tickets({}, db_path)
    counts = Counter(ticket["status"] for ticket in tickets)
    priorities = Counter(ticket["priority"] for ticket in tickets)
    projects = list_projects(db_path)
    project_ticket_counts: dict[int, int] = Counter(ticket["project_id"] for ticket in tickets)

    with connect(db_path) as conn:
        activity_rows = conn.execute(
            """
            SELECT
                e.created_at,
                e.event_type,
                e.details,
                t.id AS ticket_id,
                t.title AS ticket_title,
                p.code AS project_code,
                u.display_name AS actor_name
            FROM ticket_events e
            JOIN tickets t ON t.id = e.ticket_id
            JOIN projects p ON p.id = t.project_id
            JOIN users u ON u.id = e.actor_id
            ORDER BY e.created_at DESC
            LIMIT 8
            """
        ).fetchall()

    return {
        "ticket_total": len(tickets),
        "status_counts": dict(counts),
        "priority_counts": dict(priorities),
        "tickets_due_soon": len([ticket for ticket in tickets if ticket["status"] != "done"]),
        "project_cards": [
            {
                **project,
                "ticket_count": project_ticket_counts.get(project["id"], 0),
            }
            for project in projects
        ],
        "recent_activity": [dict(row) for row in activity_rows],
    }


def list_tickets(filters: dict[str, str] | None = None, db_path: str | Path | None = None) -> list[dict[str, Any]]:
    filters = filters or {}
    clauses = []
    params: list[Any] = []
    if filters.get("status"):
        clauses.append("t.status = ?")
        params.append(filters["status"])
    if filters.get("priority"):
        clauses.append("t.priority = ?")
        params.append(filters["priority"])
    if filters.get("assignee"):
        clauses.append("a.username = ?")
        params.append(filters["assignee"])
    if filters.get("query"):
        clauses.append("(LOWER(t.title) LIKE ? OR LOWER(t.description) LIKE ? OR LOWER(p.code) LIKE ?)")
        token = f"%{filters['query'].strip().lower()}%"
        params.extend([token, token, token])

    where_clause = ""
    if clauses:
        where_clause = "WHERE " + " AND ".join(clauses)

    with connect(db_path) as conn:
        rows = conn.execute(
            f"""
            SELECT
                t.id,
                t.project_id,
                p.code AS project_code,
                p.name AS project_name,
                t.title,
                t.description,
                t.status,
                t.priority,
                t.due_date,
                t.created_at,
                t.updated_at,
                r.display_name AS reporter_name,
                a.display_name AS assignee_name,
                a.username AS assignee_username,
                (
                    SELECT COUNT(*)
                    FROM comments c
                    WHERE c.ticket_id = t.id
                ) AS comment_count
            FROM tickets t
            JOIN projects p ON p.id = t.project_id
            JOIN users r ON r.id = t.reporter_id
            JOIN users a ON a.id = t.assignee_id
            {where_clause}
            ORDER BY
                CASE t.priority
                    WHEN 'urgent' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    ELSE 4
                END,
                t.updated_at DESC
            """,
            params,
        ).fetchall()
    return [dict(row) for row in rows]


def get_ticket(ticket_id: int, db_path: str | Path | None = None) -> dict[str, Any] | None:
    with connect(db_path) as conn:
        ticket = conn.execute(
            """
            SELECT
                t.id,
                t.project_id,
                p.code AS project_code,
                p.name AS project_name,
                t.title,
                t.description,
                t.status,
                t.priority,
                t.due_date,
                t.created_at,
                t.updated_at,
                reporter.display_name AS reporter_name,
                assignee.display_name AS assignee_name,
                assignee.username AS assignee_username
            FROM tickets t
            JOIN projects p ON p.id = t.project_id
            JOIN users reporter ON reporter.id = t.reporter_id
            JOIN users assignee ON assignee.id = t.assignee_id
            WHERE t.id = ?
            """,
            (ticket_id,),
        ).fetchone()
        if ticket is None:
            return None

        comments = conn.execute(
            """
            SELECT c.id, c.body, c.created_at, u.display_name AS author_name, u.username AS author_username
            FROM comments c
            JOIN users u ON u.id = c.author_id
            WHERE c.ticket_id = ?
            ORDER BY c.created_at ASC
            """,
            (ticket_id,),
        ).fetchall()

        events = conn.execute(
            """
            SELECT e.id, e.event_type, e.details, e.created_at, u.display_name AS actor_name
            FROM ticket_events e
            JOIN users u ON u.id = e.actor_id
            WHERE e.ticket_id = ?
            ORDER BY e.created_at DESC
            """,
            (ticket_id,),
        ).fetchall()

    payload = dict(ticket)
    payload["comments"] = [dict(row) for row in comments]
    payload["events"] = [dict(row) for row in events]
    return payload


def create_ticket(
    *,
    project_id: int,
    title: str,
    description: str,
    priority: str,
    assignee_id: int,
    due_date: str,
    reporter_id: int,
    db_path: str | Path | None = None,
) -> int:
    if priority not in PRIORITY_OPTIONS:
        raise ValueError("Invalid priority")
    with connect(db_path) as conn:
        cursor = conn.execute(
            """
            INSERT INTO tickets (
                project_id, title, description, status, priority, reporter_id,
                assignee_id, due_date, created_at, updated_at
            ) VALUES (?, ?, ?, 'todo', ?, ?, ?, ?, ?, ?)
            """,
            (project_id, title.strip(), description.strip(), priority, reporter_id, assignee_id, due_date, _now(), _now()),
        )
        ticket_id = int(cursor.lastrowid)
        conn.execute(
            "INSERT INTO ticket_events (ticket_id, actor_id, event_type, details, created_at) VALUES (?, ?, ?, ?, ?)",
            (ticket_id, reporter_id, "created", "Created a new ticket from the operations board.", _now()),
        )
        conn.commit()
        return ticket_id


def add_comment(ticket_id: int, author_id: int, body: str, db_path: str | Path | None = None) -> None:
    text = body.strip()
    if not text:
        raise ValueError("Comment body is required")
    with connect(db_path) as conn:
        conn.execute(
            "INSERT INTO comments (ticket_id, author_id, body, created_at) VALUES (?, ?, ?, ?)",
            (ticket_id, author_id, text, _now()),
        )
        conn.execute(
            "INSERT INTO ticket_events (ticket_id, actor_id, event_type, details, created_at) VALUES (?, ?, ?, ?, ?)",
            (ticket_id, author_id, "commented", "Added a follow-up comment.", _now()),
        )
        conn.execute(
            "UPDATE tickets SET updated_at = ? WHERE id = ?",
            (_now(), ticket_id),
        )
        conn.commit()


def update_ticket_status(
    ticket_id: int,
    actor_id: int,
    new_status: str,
    db_path: str | Path | None = None,
) -> None:
    if new_status not in STATUS_OPTIONS:
        raise ValueError("Invalid status")
    with connect(db_path) as conn:
        conn.execute(
            "UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?",
            (new_status, _now(), ticket_id),
            )
        conn.execute(
            "INSERT INTO ticket_events (ticket_id, actor_id, event_type, details, created_at) VALUES (?, ?, ?, ?, ?)",
            (ticket_id, actor_id, "status", f"Changed status to {new_status.replace('_', ' ')}.", _now()),
        )
        conn.commit()


def serialize_tickets(tickets: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            key: value
            for key, value in ticket.items()
            if key not in {"description"}
        }
        for ticket in tickets
    ]
