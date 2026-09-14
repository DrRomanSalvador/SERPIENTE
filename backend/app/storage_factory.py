from __future__ import annotations

import os

from .postgres_storage import PostgresRuntimeStore
from .storage import RuntimeStore


def create_runtime_store():
    dsn = os.getenv("SERPIENTE_DATABASE_URL", "").strip()
    if dsn:
        return PostgresRuntimeStore(dsn)
    return RuntimeStore(os.getenv("SERPIENTE_RUNTIME_DB", "serpiente-runtime.sqlite3"))
