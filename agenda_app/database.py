import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "agenda.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            description TEXT DEFAULT '',
            category TEXT DEFAULT 'other',
            color TEXT DEFAULT '#4A90D9',
            reminder INTEGER DEFAULT 10,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def get_all_events():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM events ORDER BY start_date").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_event_by_id(event_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM events WHERE id = ?", (event_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def save_event(event):
    conn = get_connection()
    now = datetime.now().isoformat()
    if event.get("id"):
        conn.execute("""
            UPDATE events SET title=?, start_date=?, end_date=?, description=?,
                category=?, color=?, reminder=?, updated_at=?
            WHERE id=?
        """, (
            event["title"], event["start_date"], event["end_date"],
            event.get("description", ""), event.get("category", "other"),
            event.get("color", "#4A90D9"), event.get("reminder", 10),
            now, event["id"]
        ))
    else:
        cur = conn.execute("""
            INSERT INTO events (title, start_date, end_date, description, category, color, reminder)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event["title"], event["start_date"], event["end_date"],
            event.get("description", ""), event.get("category", "other"),
            event.get("color", "#4A90D9"), event.get("reminder", 10)
        ))
        event["id"] = cur.lastrowid
    conn.commit()
    conn.close()
    return event


def delete_event(event_id):
    conn = get_connection()
    conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()


def search_events(query, category=None):
    conn = get_connection()
    sql = "SELECT * FROM events WHERE (title LIKE ? OR description LIKE ?)"
    params = [f"%{query}%", f"%{query}%"]
    if category:
        sql += " AND category = ?"
        params.append(category)
    sql += " ORDER BY start_date"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_events_by_date(date_str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM events WHERE date(start_date) = ? ORDER BY start_date",
        (date_str,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_events_in_range(start_str, end_str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM events WHERE start_date < ? AND end_date > ? ORDER BY start_date",
        (end_str, start_str)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
