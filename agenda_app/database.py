import sqlite3
import os
import sys
from datetime import datetime

if getattr(sys, "frozen", False):
    DB_DIR = os.path.dirname(sys.executable)
else:
    DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "agenda.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            task_date TEXT,
            task_time TEXT,
            priority INTEGER DEFAULT 1,
            reminder INTEGER,
            completed INTEGER DEFAULT 0,
            project TEXT DEFAULT '',
            tags TEXT DEFAULT '',
            repeat_type TEXT DEFAULT '',
            repeat_interval INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS subtasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
        );
    """)
    # Migrate columns if missing
    for col in ["repeat_type", "repeat_interval"]:
        try:
            conn.execute(f"ALTER TABLE tasks ADD COLUMN {col} TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
    try:
        conn.execute("ALTER TABLE tasks ADD COLUMN repeat_interval INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


def get_all_tasks():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE completed = 0 ORDER BY priority DESC, task_date, task_time"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_task_by_id(task_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row:
        task = dict(row)
        subtasks = conn.execute("SELECT * FROM subtasks WHERE task_id = ? ORDER BY id", (task_id,)).fetchall()
        task["subtasks"] = [dict(s) for s in subtasks]
        conn.close()
        return task
    conn.close()
    return None


def save_task(task):
    conn = get_connection()
    now = datetime.now().isoformat()
    subtasks = task.pop("subtasks", None) if task.get("id") else task.pop("subtasks", [])

    if task.get("id"):
        conn.execute("""
            UPDATE tasks SET title=?, description=?, task_date=?, task_time=?,
                priority=?, reminder=?, completed=?, project=?, tags=?,
                repeat_type=?, repeat_interval=?, updated_at=?
            WHERE id=?
        """, (
            task["title"], task.get("description", ""),
            task.get("task_date"), task.get("task_time"),
            task.get("priority", 1), task.get("reminder"),
            task.get("completed", 0), task.get("project", ""),
            task.get("tags", ""),
            task.get("repeat_type", ""), task.get("repeat_interval", 0),
            now, task["id"]
        ))
    else:
        cur = conn.execute("""
            INSERT INTO tasks (title, description, task_date, task_time, priority, reminder, completed, project, tags, repeat_type, repeat_interval)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task["title"], task.get("description", ""),
            task.get("task_date"), task.get("task_time"),
            task.get("priority", 1), task.get("reminder"),
            task.get("completed", 0), task.get("project", ""),
            task.get("tags", ""),
            task.get("repeat_type", ""), task.get("repeat_interval", 0)
        ))
        task["id"] = cur.lastrowid

    if subtasks is not None:
        conn.execute("DELETE FROM subtasks WHERE task_id = ?", (task["id"],))
        for st in subtasks:
            conn.execute(
                "INSERT INTO subtasks (task_id, title, completed) VALUES (?, ?, ?)",
                (task["id"], st.get("title", ""), st.get("completed", 0))
            )

    conn.commit()
    conn.close()
    return task


def toggle_completed(task_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if not row:
        conn.close()
        return

    task = dict(row)
    was_completed = task["completed"]

    if was_completed:
        conn.execute(
            "UPDATE tasks SET completed = 0, updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), task_id)
        )
    else:
        conn.execute(
            "UPDATE tasks SET completed = 1, updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), task_id)
        )
        create_next_occurrence(conn, task)

    conn.commit()
    conn.close()


def create_next_occurrence(conn, task):
    repeat_type = task.get("repeat_type", "")
    if not repeat_type:
        return

    from datetime import timedelta
    current_date = datetime.strptime(task["task_date"], "%Y-%m-%d") if task.get("task_date") else datetime.now()

    if repeat_type == "daily":
        next_date = current_date + timedelta(days=1)
    elif repeat_type == "weekly":
        next_date = current_date + timedelta(weeks=1)
    elif repeat_type == "monthly":
        month = current_date.month + 1
        year = current_date.year
        if month > 12:
            month = 1
            year += 1
        next_date = current_date.replace(year=year, month=month)
    elif repeat_type == "custom":
        interval = task.get("repeat_interval", 1) or 1
        next_date = current_date + timedelta(days=interval)
    else:
        return

    conn.execute("""
        INSERT INTO tasks (title, description, task_date, task_time, priority, reminder, project, tags, repeat_type, repeat_interval)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task["title"], task.get("description", ""),
        next_date.strftime("%Y-%m-%d"), task.get("task_time"),
        task.get("priority", 1), task.get("reminder"),
        task.get("project", ""), task.get("tags", ""),
        task.get("repeat_type", ""), task.get("repeat_interval", 0)
    ))


def toggle_subtask(subtask_id):
    conn = get_connection()
    conn.execute(
        "UPDATE subtasks SET completed = CASE WHEN completed THEN 0 ELSE 1 END WHERE id = ?",
        (subtask_id,)
    )
    conn.commit()
    conn.close()


def add_subtask(task_id, title):
    conn = get_connection()
    conn.execute("INSERT INTO subtasks (task_id, title) VALUES (?, ?)", (task_id, title))
    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = get_connection()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def get_tasks_by_date(date_str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE task_date = ? AND completed = 0 ORDER BY priority DESC, task_time",
        (date_str,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_tasks_by_date_range(start_str, end_str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE task_date >= ? AND task_date <= ? AND completed = 0 ORDER BY task_date, priority DESC, task_time",
        (start_str, end_str)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_today_tasks():
    today = datetime.now().strftime("%Y-%m-%d")
    return get_tasks_by_date(today)


def get_high_priority_tasks():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE priority = 2 AND completed = 0 ORDER BY task_date, task_time"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_overdue_tasks():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE task_date < ? AND task_date IS NOT NULL AND completed = 0 ORDER BY task_date",
        (today,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def search_tasks(query, priority=None, completed=0, project=None):
    conn = get_connection()
    sql = "SELECT * FROM tasks WHERE (title LIKE ? OR description LIKE ?) AND completed = ?"
    params = [f"%{query}%", f"%{query}%", 1 if completed else 0]
    if priority is not None:
        sql += " AND priority = ?"
        params.append(priority)
    if project:
        sql += " AND project = ?"
        params.append(project)
    sql += " ORDER BY priority DESC, task_date, task_time"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_projects():
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT project FROM tasks WHERE project != '' ORDER BY project").fetchall()
    conn.close()
    return [r["project"] for r in rows]


def get_tasks_no_date():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE (task_date IS NULL OR task_date = '') AND completed = 0 ORDER BY priority DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
