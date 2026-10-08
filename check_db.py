import sqlite3
conn = sqlite3.connect(r'D:\西客松\backend\data\flowforge.db')
c = conn.cursor()
tables = ['score_records', 'executions', 'node_executions', 'token_usage', 'cost_records', 'workflows', 'agent_templates', 'marketplace_items']
for t in tables:
    try:
        cnt = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {cnt}")
    except Exception as e:
        print(f"  {t}: ERROR {e}")
if c.execute("SELECT COUNT(*) FROM score_records").fetchone()[0] == 0:
    print("  WARNING: score_records is empty!")
if c.execute("SELECT COUNT(*) FROM executions").fetchone()[0] == 0:
    print("  WARNING: executions is empty!")
conn.close()