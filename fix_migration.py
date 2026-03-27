import sqlite3

conn = sqlite3.connect('fitroom_fresh.db')
cursor = conn.cursor()

# Mark the migration as applied
cursor.execute('UPDATE alembic_version SET version_num = "8ce965d5eb18"')
conn.commit()

print("Migration marked as applied")

conn.close()