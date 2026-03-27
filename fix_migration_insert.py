import sqlite3

conn = sqlite3.connect('fitroom_fresh.db')
cursor = conn.cursor()

# Insert the migration version
cursor.execute('INSERT INTO alembic_version (version_num) VALUES ("8ce965d5eb18")')
conn.commit()

print("Migration version inserted")

conn.close()