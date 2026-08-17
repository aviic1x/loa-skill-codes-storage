"""SQLite persistence layer: schema, connection, CRUD, search.

Plain sqlite3, no ORM: rows are sqlite3.Row (accessed by column name),
which is enough for an app of this size.
"""
import re
import sqlite3

from app.paths import get_db_path
from app.seed_data import DEFAULT_CLASSES

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS classes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL UNIQUE,
    slug          TEXT NOT NULL UNIQUE,
    icon_filename TEXT,
    is_favorite   INTEGER NOT NULL DEFAULT 0,
    sort_order    INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS skill_codes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id    INTEGER NOT NULL,
    name        TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    code        TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_skill_codes_class_id ON skill_codes(class_id);
"""


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")
    return slug or "class"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()
    _migrate_schema(conn)
    seed_if_empty(conn)


def _migrate_schema(conn: sqlite3.Connection) -> None:
    """Adds columns introduced after the initial release to databases that
    already exist on disk, so existing user data is never lost."""
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(classes)").fetchall()}
    if "is_favorite" not in columns:
        conn.execute("ALTER TABLE classes ADD COLUMN is_favorite INTEGER NOT NULL DEFAULT 0")
        conn.commit()


def seed_if_empty(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) FROM classes").fetchone()[0]
    if count:
        return
    for order, name in enumerate(DEFAULT_CLASSES):
        slug = slugify(name)
        conn.execute(
            "INSERT INTO classes (name, slug, icon_filename, sort_order) "
            "VALUES (?, ?, ?, ?)",
            (name, slug, f"{slug}.png", order),
        )
    conn.commit()


# ---- Classes -----------------------------------------------------------

def list_classes(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM classes ORDER BY is_favorite DESC, sort_order, name"
    ).fetchall()


def get_class(conn: sqlite3.Connection, class_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM classes WHERE id = ?", (class_id,)
    ).fetchone()


def add_class(conn: sqlite3.Connection, name: str, icon_filename: str | None = None) -> int:
    slug = slugify(name)
    max_order = conn.execute(
        "SELECT COALESCE(MAX(sort_order), -1) FROM classes"
    ).fetchone()[0]
    cur = conn.execute(
        "INSERT INTO classes (name, slug, icon_filename, sort_order) "
        "VALUES (?, ?, ?, ?)",
        (name, slug, icon_filename or f"{slug}.png", max_order + 1),
    )
    conn.commit()
    return cur.lastrowid


def update_class(
    conn: sqlite3.Connection,
    class_id: int,
    name: str | None = None,
    icon_filename: str | None = None,
) -> None:
    fields, params = [], []
    if name is not None:
        fields.append("name = ?")
        params.append(name)
    if icon_filename is not None:
        fields.append("icon_filename = ?")
        params.append(icon_filename)
    if not fields:
        return
    fields.append("updated_at = datetime('now')")
    params.append(class_id)
    conn.execute(f"UPDATE classes SET {', '.join(fields)} WHERE id = ?", params)
    conn.commit()


def delete_class(conn: sqlite3.Connection, class_id: int) -> None:
    conn.execute("DELETE FROM classes WHERE id = ?", (class_id,))
    conn.commit()


def set_class_favorite(conn: sqlite3.Connection, class_id: int, is_favorite: bool) -> None:
    conn.execute(
        "UPDATE classes SET is_favorite = ?, updated_at = datetime('now') WHERE id = ?",
        (1 if is_favorite else 0, class_id),
    )
    conn.commit()


# ---- Skill codes ---------------------------------------------------------

def list_skill_codes(conn: sqlite3.Connection, class_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM skill_codes WHERE class_id = ? ORDER BY name",
        (class_id,),
    ).fetchall()


def add_skill_code(
    conn: sqlite3.Connection, class_id: int, name: str, description: str, code: str
) -> int:
    cur = conn.execute(
        "INSERT INTO skill_codes (class_id, name, description, code) "
        "VALUES (?, ?, ?, ?)",
        (class_id, name, description, code),
    )
    conn.commit()
    return cur.lastrowid


def update_skill_code(
    conn: sqlite3.Connection, skill_code_id: int, name: str, description: str, code: str
) -> None:
    conn.execute(
        "UPDATE skill_codes SET name = ?, description = ?, code = ?, "
        "updated_at = datetime('now') WHERE id = ?",
        (name, description, code, skill_code_id),
    )
    conn.commit()


def delete_skill_code(conn: sqlite3.Connection, skill_code_id: int) -> None:
    conn.execute("DELETE FROM skill_codes WHERE id = ?", (skill_code_id,))
    conn.commit()


def search_skill_codes(conn: sqlite3.Connection, query: str) -> list[sqlite3.Row]:
    like = f"%{query.lower()}%"
    return conn.execute(
        """
        SELECT sc.*, c.name AS class_name, c.icon_filename
        FROM skill_codes sc
        JOIN classes c ON c.id = sc.class_id
        WHERE lower(sc.name) LIKE ? OR lower(sc.description) LIKE ?
        ORDER BY c.name, sc.name
        """,
        (like, like),
    ).fetchall()
