import sqlite3
conn = sqlite3.connect(r'D:\西客松\backend\data\flowforge.db')
c = conn.cursor()
c.execute("PRAGMA table_info(marketplace_items)")
for col in c.fetchall():
    print(col)
conn.close()