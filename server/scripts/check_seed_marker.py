# -*- coding: utf-8 -*-
"""
检查 sqlite 数据库中是否存在包含“种子”字样的 mind_knowledge 记录。
运行方式：在项目 server 目录下使用虚拟环境的 python 运行本脚本。
"""
import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent.parent / 'july_dev.db'
if not db_path.exists():
    print('DB not found at', db_path)
    raise SystemExit(1)

conn = sqlite3.connect(str(db_path))
cur = conn.cursor()
q = "select id, title from mind_knowledge where title like '%种子%' or content like '%种子%' or source like '%种子%';"
cur.execute(q)
rows = cur.fetchall()
print('DB:', db_path)
print('matches:', len(rows))
for r in rows[:20]:
    print('-', r[0], r[1])
conn.close()
