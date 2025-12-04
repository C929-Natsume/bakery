#!/usr/bin/env python3
"""
把清洗后的 JSONL 转换为 mind_seed.sql 的 INSERT 语句文件。
输入： `../data/clean_wenda.jsonl` 或任意类似结构的 JSONL，每行包含 url, title, content, id(optional)
输出： `../sql/mind_seed.generated.sql`

注意：脚本会保留原有 WHERE NOT EXISTS 风格，以避免重复插入。
"""

import argparse
import html
import json
import os
import re
import sys
from urllib.parse import urlparse

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'sql')
os.makedirs(OUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUT_DIR, 'mind_seed.generated.sql')

TEMPLATE = """
INSERT INTO `mind_knowledge` (`id`, `title`, `content`, `tags`, `source`, `created_at`) 
SELECT REPLACE(UUID(),'-',''), '{title}', '{content}', '{tags}', '{source}', NOW() 
FROM DUAL WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title = '{title_esc}');
"""


def escape_sql_value(s):
    if s is None:
        return ''
    # collapse multiple blank lines
    s = re.sub(r"\r\n|\r", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    # escape single quote for SQL
    s = s.replace("'", "\\'")
    # strip too long
    return s


def read_jsonl(path):
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', default=os.path.join(os.path.dirname(__file__), '..', 'data', 'clean_wenda.jsonl'))
    p.add_argument('--output', default=OUT_FILE)
    args = p.parse_args()

    entries = list(read_jsonl(args.input))
    if not entries:
        print('No entries found in', args.input)
        sys.exit(1)

    with open(args.output, 'w', encoding='utf-8') as out:
        out.write('-- Generated mind_seed SQL\n')
        out.write('SET NAMES utf8mb4;\n')
        for e in entries:
            title = e.get('title') or ''
            content = e.get('content') or ''
            source = e.get('source') or e.get('url') or ''
            # simple tag heuristic: source domain or '心理'
            domain = urlparse(e.get('url', '')).hostname or ''
            tags = '心理' if 'xinlixue' in source or 'xinli' in domain else ''

            title_esc = escape_sql_value(title)
            content_esc = escape_sql_value(content)
            tags_esc = escape_sql_value(tags)
            source_esc = escape_sql_value(source)

            sql = TEMPLATE.format(title=title_esc, content=content_esc, tags=tags_esc, source=source_esc, title_esc=title_esc)
            out.write(sql + '\n')

    print('Generated SQL written to', args.output)
    print('Tip: review the file before importing. Backup original mind_seed.sql if needed.')


if __name__ == '__main__':
    main()
