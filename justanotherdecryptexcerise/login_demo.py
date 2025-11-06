import sqlite3, bcrypt, getpass, os

DB_PATH = os.environ.get("STUDENTS_DB", "students.db")

def check_login(conn, username, password_plain):
    cur = conn.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    if not row:
        return False
    stored_hash = row[0].encode("utf-8")
    return bcrypt.checkpw(password_plain.encode("utf-8"), stored_hash)

def main():
    print("=== Login Demo ===")
    conn = sqlite3.connect(DB_PATH)
    try:
        username = input("Username: ").strip()
        password = getpass.getpass("Password (input hidden): ")
        ok = check_login(conn, username, password)
        if ok:
            print("✅ Login successful!")
        else:
            print("❌ Invalid username or password.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()