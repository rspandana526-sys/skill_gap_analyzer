from database import get_db


def username_exists(username):
    conn = get_db()
    row = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return row is not None


def save_user(username, password, email=None, phone=None):
    """
    Returns:
        True   – user created successfully
        'dup'  – username already taken
        False  – unexpected error
    """
    try:
        if username_exists(username):
            return 'dup'

        conn = get_db()
        conn.execute(
            "INSERT INTO users (username, password, email, phone) VALUES (?,?,?,?)",
            (username, password, email, phone)
        )
        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"[AUTH] Error saving user: {type(e).__name__}: {e}")
        return False


def validate_user(username, password):
    try:
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?", (username, password)
        ).fetchone()
        conn.close()
        return row is not None
    except Exception as e:
        print(f"[AUTH] Error validating user: {e}")
        return False


def verify_current_password(username, password):
    return validate_user(username, password)
