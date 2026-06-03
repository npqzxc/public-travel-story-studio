from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = BASE_DIR / "data"


@dataclass(frozen=True)
class Settings:
    host: str = os.getenv("OPS_DESK_HOST", "0.0.0.0")
    port: int = int(os.getenv("OPS_DESK_PORT", "8000"))
    session_secret: str = os.getenv("OPS_DESK_SESSION_SECRET", "travel-editor-dev-secret")
    data_dir: Path = Path(os.getenv("OPS_DESK_DATA_DIR", str(DEFAULT_DATA_DIR)))
    db_path: Path = Path(os.getenv("OPS_DESK_DB_PATH", str(DEFAULT_DATA_DIR / "ops_desk.sqlite3")))
    cookie_name: str = "opsdesk_session"


SETTINGS = Settings()
