import sqlite3

conn = sqlite3.connect("instance/bugtracker.db")
cursor = conn.cursor()

try:
    cursor.execute(
        "ALTER TABLE bug ADD COLUMN bug_source TEXT DEFAULT 'Testing Team'"
    )
    print("bug_source added")
except Exception as e:
    print("bug_source:", e)

try:
    cursor.execute(
        "ALTER TABLE bug ADD COLUMN created_by_id INTEGER"
    )
    print("created_by_id added")
except Exception as e:
    print("created_by_id:", e)

conn.commit()
conn.close()

print("Database updated successfully")
