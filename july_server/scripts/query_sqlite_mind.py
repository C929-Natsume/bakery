import sqlite3
import os

DB_PATHS = [
    os.path.join(os.path.dirname(__file__), '..', 'july_dev.db'),
    os.path.join(os.path.dirname(__file__), '..', 'app_2', 'july_dev.db'),
    os.path.join(os.path.dirname(__file__), '..', 'app_2', '..', 'july_dev.db'),
]

def find_db():
    for p in DB_PATHS:
        p = os.path.abspath(p)
        if os.path.exists(p):
            return p
    return None


def main():
    db = find_db()
    if not db:
        print('No july_dev.db found in expected locations.')
        return
    print('Using DB:', db)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        print('Tables:', tables)
        if 'mind_knowledge' in tables:
            cur.execute('SELECT id,title, LENGTH(content) as len, substr(content,1,300) FROM mind_knowledge LIMIT 10')
            rows = cur.fetchall()
            print('Found', len(rows), 'rows in mind_knowledge')
            for r in rows:
                print('---')
                print('id:', r[0])
                print('title:', r[1])
                print('content_len:', r[2])
                print('content_preview:', r[3])
        else:
            print('No mind_knowledge table found. You can seed using scripts/seed_mind.py or import SQL.')
    finally:
        conn.close()

if __name__ == '__main__':
    main()
