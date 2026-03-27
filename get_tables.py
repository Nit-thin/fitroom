import sqlite3

# Connect to the database
con = sqlite3.connect('fitroom_fresh.db')
cur = con.cursor()

# Get all table names
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]

print("TABLES IN YOUR PROJECT:")
print("="*50)
for i, table in enumerate(tables, 1):
    print(f"{i}. {table}")

print("\nDETAILED TABLE STRUCTURE:")
print("="*50)

for table in tables:
    cur.execute(f"PRAGMA table_info({table})")
    cols = cur.fetchall()
    
    print(f"\n{table.upper()}:")
    print("-" * 30)
    
    for col in cols:
        col_id, name, data_type, not_null, default_val, pk = col
        constraints = []
        if pk:
            constraints.append("PK")
        if not_null:
            constraints.append("NOT NULL")
        if default_val is not None:
            constraints.append(f"DEFAULT {default_val}")
        
        constraint_str = " - " + " ".join(constraints) if constraints else ""
        print(f"  {name} ({data_type}){constraint_str}")

con.close()

