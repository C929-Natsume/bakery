#!/usr/bin/env python3
"""
简单的 SQL 文件导入脚本（用于 Windows PowerShell 环境，当没有 mysql 客户端可用时）。
用法：
  python import_sql_file.py --user root --password secret --host 127.0.0.1 --port 3306 --db july --file "..\..\sql\mind_seed.sql"

可选：添加 --binary-uuid 参数会在执行前把 REPLACE(UUID(),'-','') 替换为 UNHEX(REPLACE(UUID(),'-',''))，用于表的 id 为 BINARY(16) 的情况。

依赖：pip install pymysql
"""

import argparse
import pymysql
import sys
import re


def parse_args():
    p = argparse.ArgumentParser(description='Import SQL file into MySQL using pymysql')
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=3306)
    p.add_argument('--user', required=True)
    p.add_argument('--password', required=True)
    p.add_argument('--db', required=True)
    p.add_argument('--file', required=True)
    p.add_argument('--binary-uuid', action='store_true', help='Replace REPLACE(UUID(),"-","") with UNHEX(REPLACE(UUID(),"-","")).')
    return p.parse_args()


def load_sql(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def split_statements(sql):
    # remove -- comments and /* */ comments
    sql = re.sub(r'--.*?\n', '\n', sql)
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.S)
    # naive split by semicolon
    parts = [s.strip() for s in sql.split(';') if s.strip()]
    return parts


def main():
    args = parse_args()
    raw = load_sql(args.file)
    if args.binary_uuid:
        raw = raw.replace("REPLACE(UUID(),'-','')", "UNHEX(REPLACE(UUID(),'-',''))")
    stmts = split_statements(raw)
    print(f'Loaded SQL file {args.file}, detected {len(stmts)} statements (approx).')

    try:
        conn = pymysql.connect(host=args.host, port=args.port, user=args.user, password=args.password, db=args.db, charset='utf8mb4', autocommit=True)
        cursor = conn.cursor()
        i = 0
        for s in stmts:
            i += 1
            try:
                cursor.execute(s)
            except Exception as e:
                print(f'Error executing statement #{i}:', e)
                print('Statement preview:', s[:200].replace('\n',' '))
                # stop on error
                cursor.close()
                conn.close()
                sys.exit(1)
        cursor.close()
        conn.close()
        print('Import completed successfully.')
    except Exception as e:
        print('DB connection or execution failed:', e)
        sys.exit(2)


if __name__ == '__main__':
    main()
