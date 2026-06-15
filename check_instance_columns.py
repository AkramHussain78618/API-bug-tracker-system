import sqlite3

conn = sqlite3.connect("instance/bugtracker.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(bug)")

for column in cursor.fetchall():
	print(column)

conn.close()
