#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export SEEDS defined in `scripts/seed_mind.py` into a SQL file with
INSERT-if-not-exists blocks. This avoids importing the module to prevent
side effects (it parses the literal `SEEDS` from the file).

Usage (from project root):
  python scripts\export_seed_to_sql.py

Output:
  ./server/sql/mind_seed_from_script.utf8.sql
"""
import ast
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_FILE = os.path.join(ROOT, 'scripts', 'seed_mind.py')
OUT_SQL = os.path.join(ROOT, 'sql', 'mind_seed_from_script.utf8.sql')

def extract_seeds(text: str):
    # Find the start of the SEEDS assignment
    m = re.search(r"SEEDS\s*=\s*\[", text)
    if not m:
        raise RuntimeError('SEEDS list not found in seed_mind.py')
    start = m.start()
    # find the opening bracket position
    open_idx = text.find('[', start)
    # bracket matching to find the end
    i = open_idx
    depth = 0
    while i < len(text):
        ch = text[i]
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                end_idx = i
                break
        i += 1
    else:
        raise RuntimeError('Could not find matching closing ] for SEEDS')
    seeds_literal = text[open_idx:end_idx+1]
    # Use ast.literal_eval to safely evaluate the list literal
    return ast.literal_eval(seeds_literal)

def sql_escape(s: str) -> str:
    if s is None:
        return 'NULL'
    # replace single quote with two single quotes for SQL
    return "'" + s.replace("'", "''") + "'"

def json_str(tags):
    import json
    return json.dumps(tags, ensure_ascii=False)

def make_insert_block(seed: dict) -> str:
    title = seed.get('title', '')
    content = seed.get('content', '')
    tags = seed.get('tags') or []
    source = seed.get('source') or ''
    category = seed.get('category') or ''
    read_count = seed.get('read_count') or 0

    parts = []
    parts.append('INSERT INTO mind_knowledge (id, title, tags, source, category, content, read_count)')
    parts.append('SELECT REPLACE(UUID(),"-",""),')
    parts.append('       {title},'.format(title=sql_escape(title)))
    parts.append('       {tags},'.format(tags=sql_escape(json_str(tags))))
    parts.append('       {source},'.format(source=sql_escape(source)))
    parts.append('       {category},'.format(category=sql_escape(category)))
    parts.append('       {content},'.format(content=sql_escape(content)))
    parts.append('       {rc}'.format(rc=int(read_count)))
    parts.append('FROM DUAL')
    parts.append('WHERE NOT EXISTS (SELECT 1 FROM mind_knowledge WHERE title = {title});'.format(title=sql_escape(title)))
    return '\n'.join(parts)

def main():
    with io.open(SEED_FILE, 'r', encoding='utf-8') as f:
        text = f.read()

    seeds = extract_seeds(text)
    blocks = []
    for s in seeds:
        blocks.append('-- --------------------------------------------------')
        blocks.append(make_insert_block(s))

    header = '-- Generated from scripts/seed_mind.py\n-- INSERT-if-not-exists for each seed\n-- Encoding: UTF-8\n\n'
    os.makedirs(os.path.dirname(OUT_SQL), exist_ok=True)
    with io.open(OUT_SQL, 'w', encoding='utf-8') as out:
        out.write(header)
        out.write('\n\n'.join(blocks))

    print('Wrote:', OUT_SQL)

if __name__ == '__main__':
    main()
