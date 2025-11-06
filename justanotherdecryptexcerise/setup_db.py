import csv, sqlite3, bcrypt, datetime, os, sys

DB_PATH = os.environ.get("STUDENTS_DB", "students.db")
CSV_PATH = os.environ.get("STUDENTS_CSV", "students.csv")
ROUNDS = int(os.environ.get("BCRYPT_ROUNDS", "12"))

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
    pw_bytes = password_plain.encode("utf-8")
    hashed = bcrypt.hashpw(pw_bytes, bcrypt.gensalt(rounds=ROUNDS))
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO users (username, email, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?)",
        (username, email, hashed.decode("utf-8"), "student", datetime.datetime.now().isoformat(timespec="seconds"))
    )
    conn.commit()

def main():
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: CSV file not found at {CSV_PATH}", file=sys.stderr)
        sys.exit(1)
    conn = sqlite3.connect(DB_PATH)
    ensure_db(conn)

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            username = row["username"].strip()
            email = row["email"].strip()
            temp_password = row["temp_password"]
            add_user(conn, username, email, temp_password)
            count += 1
            print(f"Added: {username}")
    print(f"✅ Done. Inserted/updated {count} users into {DB_PATH}. Bcrypt rounds={ROUNDS}.")

if __name__ == "__main__":
    main()