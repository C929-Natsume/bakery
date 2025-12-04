import sqlite3,os
p='july_dev.db'
print('exists', os.path.exists(p))
if not os.path.exists(p):
    raise SystemExit(0)
con=sqlite3.connect(p)
cur=con.cursor()
# list tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('tables:', cur.fetchall())
# try to read mind related tables: mind_knowledge or mind_category
for t in ('mind_knowledge','mind_category','mind_meta','mind_categories'):
    try:
        cur.execute(f"SELECT count(1) FROM {t}")
        print(t, cur.fetchone())
    except Exception as e:
        print(t, 'err', e)
# try to show first rows of mind_knowledge
try:
    cur.execute("SELECT id,title,category,tag FROM mind_knowledge LIMIT 5")
    rows=cur.fetchall()
    print('mind_knowledge rows:', rows)
except Exception as e:
    print('mind_knowledge err', e)
con.close()
