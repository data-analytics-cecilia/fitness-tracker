import sqlite3
from pathlib import Path

DB_PATH = Path("db/app.db")

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        user TEXT PRIMARY KEY,
        steps_target INTEGER,
        sleep_target REAL,
        hr_max_target INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS events (
        user TEXT PRIMARY KEY,
        storm_on INTEGER
    )
    """)

    conn.commit()
    conn.close()

def load_settings(user: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT steps_target, sleep_target, hr_max_target FROM settings WHERE user=?", (user,))
    row = c.fetchone()
    conn.close()

    if row is None:
        return {"steps_target": 10000, "sleep_target": 7.5, "hr_max_target": 85}
    return {"steps_target": row[0], "sleep_target": row[1], "hr_max_target": row[2]}

def save_settings(user: str, steps_target: int, sleep_target: float, hr_max_target: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO settings(user, steps_target, sleep_target, hr_max_target)
        VALUES(?,?,?,?)
        ON CONFLICT(user) DO UPDATE SET
            steps_target=excluded.steps_target,
            sleep_target=excluded.sleep_target,
            hr_max_target=excluded.hr_max_target
    """, (user, steps_target, sleep_target, hr_max_target))
    conn.commit()
    conn.close()

def load_storm(user: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT storm_on FROM events WHERE user=?", (user,))
    row = c.fetchone()
    conn.close()
    return bool(row[0]) if row else False

def save_storm(user: str, storm_on: bool):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO events(user, storm_on)
        VALUES(?,?)
        ON CONFLICT(user) DO UPDATE SET storm_on=excluded.storm_on
    """, (user, int(storm_on)))
    conn.commit()
    conn.close()
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000