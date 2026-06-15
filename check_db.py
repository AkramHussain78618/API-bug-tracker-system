import os
import sqlite3

print("Current folder:", os.getcwd())

db_path = "bugtracker.db"

print("Database exists:", os.path.exists(db_path))

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute(
"SELECT name FROM sqlite_master WHERE type='table';"
)

print("Tables:")
print(cursor.fetchall())

conn.close()
