import sqlite3, os

DB_PATH = os.environ.get("STUDENTS_DB", "students.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT id, username, email, role, created_at, password_hash FROM users ORDER BY id")
rows = cur.fetchall()

print("id | username | email | role | created_at | password_hash")
print("-"*90)
for r in rows:
    print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]}")

conn.close()