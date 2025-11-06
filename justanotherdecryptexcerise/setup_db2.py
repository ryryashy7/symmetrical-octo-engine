import csv
import sqlite3
import datetime
import os
import sys

try:
    import bcrypt
except Exception:
    print("ERROR: missing dependency 'bcrypt'. Install with: pip install bcrypt", file=sys.stderr)
    sys.exit(1)

DB_PATH = os.environ.get("STUDENTS_DB", "students.db")
CSV_PATH = os.environ.get("STUDENTS_CSV", "students.csv")
try:
    ROUNDS = int(os.environ.get("BCRYPT_ROUNDS", "12"))
except ValueError:
    ROUNDS = 12

def ensure_db(conn):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student',
        created_at TEXT NOT NULL
    )
    """)
    conn.commit()

def add_user(conn, username, email, password_plain):
    if not username or not email:
        raise ValueError("username and email are required")
    if not password_plain:
        raise ValueError(f"empty password for user '{username}'")

    pw_bytes = password_plain.encode("utf-8")
    hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt(rounds=ROUNDS)).decode("utf-8")

    cur = conn.cursor()
    try:
        # Use upsert to preserve id when username already exists (SQLite 3.24+)
        cur.execute("""
        INSERT INTO users (username, email, password_hash, role, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            email=excluded.email,
            password_hash=excluded.password_hash,
            role=excluded.role,
            created_at=excluded.created_at
        """, (username, email, hashed, "student", datetime.datetime.now().isoformat(timespec="seconds")))
    except sqlite3.OperationalError:
        # Fallback for older SQLite: replace (will change id)
        cur.execute(
            "INSERT OR REPLACE INTO users (username, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (username, email, hashed, "student", datetime.datetime.now().isoformat(timespec="seconds"))
        )
    conn.commit()

def main():
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: CSV file not found at {CSV_PATH}", file=sys.stderr)
        sys.exit(1)

    with sqlite3.connect(DB_PATH) as conn:
        ensure_db(conn)

        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            required = {"username", "email", "temp_password"}
            if not required.issubset(set(reader.fieldnames or [])):
                print(f"ERROR: CSV must contain headers: {', '.join(sorted(required))}", file=sys.stderr)
                sys.exit(1)

            count = 0
            for i, row in enumerate(reader, start=1):
                username = (row.get("username") or "").strip()
                email = (row.get("email") or "").strip()
                temp_password = (row.get("temp_password") or "").strip()

                if not username or not email or not temp_password:
                    print(f"Skipping line {i}: missing username/email/password", file=sys.stderr)
                    continue

                try:
                    add_user(conn, username, email, temp_password)
                    count += 1
                    print(f"Added/updated: {username}")
                except Exception as e:
                    print(f"ERROR adding {username}: {e}", file=sys.stderr)

    print(f"✅ Done. Inserted/updated {count} users into {DB_PATH}. Bcrypt rounds={ROUNDS}.")
    return 0

if __name__ == "__main__":
    sys.exit(main())