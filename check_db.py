import sqlite3

conn = sqlite3.connect('fitroom_fresh.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in database:", tables)

# Check if alembic_version table exists
if 'alembic_version' in tables:
    cursor.execute("SELECT version_num FROM alembic_version")
    version = cursor.fetchone()
    print("Alembic version:", version[0] if version else "None")
else:
    print("No alembic_version table found")

conn.close()