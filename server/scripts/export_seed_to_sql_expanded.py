#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export SEEDS from `scripts/seed_mind.py`, expand `content` using
`app_2.lib.mind_content_generator.generate_content`, and write a UTF-8 SQL file.

Usage (from project root):
  python server/scripts/export_seed_to_sql_expanded.py

Output:
  ./server/sql/mind_seed_from_script.expanded.utf8.sql
"""
import ast
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_FILE = os.path.join(ROOT, 'scripts', 'seed_mind.py')
OUT_SQL = os.path.join(ROOT, 'sql', 'mind_seed_from_script.expanded.utf8.sql')


def extract_seeds(text: str):
    m = re.search(r"SEEDS\s*=\s*\[", text)
    if not m:
        raise RuntimeError('SEEDS list not found in seed_mind.py')
    start = m.start()
    open_idx = text.find('[', start)
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
    return ast.literal_eval(seeds_literal)


def sql_escape(s: str) -> str:
    if s is None:
        return 'NULL'
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

    # Import generator without importing the whole package (avoid side effects)
    generate_content = None
    try:
        import runpy
        mg_path = os.path.join(ROOT, 'app_2', 'lib', 'mind_content_generator.py')
        if os.path.exists(mg_path):
            mod_globals = runpy.run_path(mg_path)
            generate_content = mod_globals.get('generate_content')
        else:
            # fallback to app/lib
            mg_path2 = os.path.join(ROOT, 'app', 'lib', 'mind_content_generator.py')
            if os.path.exists(mg_path2):
                mod_globals = runpy.run_path(mg_path2)
                generate_content = mod_globals.get('generate_content')
    except Exception:
        generate_content = None

    if not generate_content:
        raise RuntimeError('Could not load generate_content from app_2/lib or app/lib')

    blocks = []
    for s in seeds:
        # Expand content using generator (safe: generator returns str)
        try:
            s['content'] = generate_content(s.get('title'), s.get('tags', []), s.get('source'))
        except Exception:
            # keep existing if generator fails
            pass
        blocks.append('-- --------------------------------------------------')
        blocks.append(make_insert_block(s))

    header = '-- Generated (expanded) from scripts/seed_mind.py\n-- INSERT-if-not-exists for each seed\n-- Encoding: UTF-8\n\n'
    os.makedirs(os.path.dirname(OUT_SQL), exist_ok=True)
    with io.open(OUT_SQL, 'w', encoding='utf-8') as out:
        out.write(header)
        out.write('\n\n'.join(blocks))

    print('Wrote:', OUT_SQL)


if __name__ == '__main__':
    main()
