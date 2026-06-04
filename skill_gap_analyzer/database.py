import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "skillgap.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(app=None):
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email    TEXT,
            phone    TEXT
        );

        CREATE TABLE IF NOT EXISTS history (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role     TEXT,
            score    INTEGER,
            missing  TEXT,
            date     DATETIME DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS learned_skills (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            skills   TEXT
        );

        CREATE TABLE IF NOT EXISTS otp_store (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            contact    TEXT NOT NULL,
            otp        TEXT NOT NULL,
            created_at DATETIME DEFAULT (datetime('now'))
        );
    """)

    conn.commit()
    conn.close()
    print("✅ SQLite database ready.")


# ── OTP ──────────────────────────────────────────────────────────────────────

def save_otp(contact, otp):
    conn = get_db()
    conn.execute("DELETE FROM otp_store WHERE contact=?", (contact,))
    conn.execute("INSERT INTO otp_store (contact, otp) VALUES (?,?)", (contact, otp))
    conn.commit()
    conn.close()


def verify_otp(contact, otp):
    conn = get_db()
    row = conn.execute("""
        SELECT * FROM otp_store
        WHERE contact=? AND otp=?
        AND created_at >= datetime('now', '-10 minutes')
    """, (contact, otp)).fetchone()
    if row:
        conn.execute("DELETE FROM otp_store WHERE contact=?", (contact,))
        conn.commit()
    conn.close()
    return row is not None


def get_user_by_email(email):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_phone(phone):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE phone=?", (phone,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_password(username, new_password):
    conn = get_db()
    conn.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
    conn.commit()
    conn.close()


# ── HISTORY ──────────────────────────────────────────────────────────────────

def save_history(username, role, score, missing):
    missing_str = ", ".join(missing)
    conn = get_db()
    conn.execute(
        "INSERT INTO history (username, role, score, missing) VALUES (?,?,?,?)",
        (username, role, score, missing_str)
    )
    conn.commit()
    conn.close()


def get_history(username):
    conn = get_db()
    rows = conn.execute(
        "SELECT role, score, missing, date FROM history WHERE username=? ORDER BY id ASC",
        (username,)
    ).fetchall()
    conn.close()
    return [
        {
            "role":    r["role"],
            "score":   r["score"],
            "missing": r["missing"].split(", ") if r["missing"] else [],
            "date":    str(r["date"])
        }
        for r in rows
    ]


def clear_history(username):
    conn = get_db()
    conn.execute("DELETE FROM history WHERE username=?", (username,))
    conn.commit()
    conn.close()


def delete_history_item(username, index):
    conn = get_db()
    rows = conn.execute(
        "SELECT id FROM history WHERE username=? ORDER BY id ASC", (username,)
    ).fetchall()
    if 0 <= index < len(rows):
        conn.execute("DELETE FROM history WHERE id=?", (rows[index]["id"],))
        conn.commit()
    conn.close()


def get_total_analyses(username):
    conn = get_db()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM history WHERE username=?", (username,)
    ).fetchone()
    conn.close()
    return row["cnt"] if row else 0


def change_password(username, new_password):
    conn = get_db()
    conn.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
    conn.commit()
    conn.close()
    return True


# ── LEARNED SKILLS ───────────────────────────────────────────────────────────

def get_learned_skills(username):
    conn = get_db()
    row = conn.execute(
        "SELECT skills FROM learned_skills WHERE username=?", (username,)
    ).fetchone()
    conn.close()
    if row and row["skills"]:
        return row["skills"].split(",")
    return []


def save_learned_skills(username, skills):
    skills_str = ",".join(skills)
    conn = get_db()
    row = conn.execute(
        "SELECT id FROM learned_skills WHERE username=?", (username,)
    ).fetchone()
    if row:
        conn.execute(
            "UPDATE learned_skills SET skills=? WHERE username=?", (skills_str, username)
        )
    else:
        conn.execute(
            "INSERT INTO learned_skills (username, skills) VALUES (?,?)", (username, skills_str)
        )
    conn.commit()
    conn.close()
    return True
