import sqlite3

conn = sqlite3.connect('fitroom_fresh.db')
cursor = conn.cursor()

# Check alembic_version table content
cursor.execute("SELECT * FROM alembic_version")
result = cursor.fetchall()
print("alembic_version table content:", result)

conn.close()