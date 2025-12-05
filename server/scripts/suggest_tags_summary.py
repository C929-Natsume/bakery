#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scan mind_knowledge rows that have generic tag '心理' (or empty tags),
generate suggested tags and a summary/category, and write SQL update
statements to sql/update_mind_suggestions.sql for manual review.

Usage: python suggest_tags_summary.py
"""
import json
import re
import os
import sys
try:
    import jieba
    has_jieba = True
except Exception:
    has_jieba = False
import pymysql

DB = dict(host='127.0.0.1', user='root', password='lyy20041218', db='july', charset='utf8mb4')

OUT_SQL = os.path.join(os.path.dirname(__file__), '..', 'sql', 'update_mind_suggestions.sql')

def simple_extract(text, topn=2):
    if not text:
        return []
    # extract continuous Chinese sequences
    segs = re.findall(r'[\u4e00-\u9fa5]{2,}', text)
    freq = {}
    for s in segs:
        freq[s] = freq.get(s,0)+1
    keys = sorted(freq.keys(), key=lambda k:(-freq[k], -len(k)))
    out = []
    for k in keys:
        if re.match(r'^(文章|本文|示例|方法|包括|通常|可能|我们)$', k):
            continue
        out.append(k)
        if len(out)>=topn:
            break
    if out:
        return out
    return segs[:topn]

def jieba_extract(text, topn=2):
    segs = [w for w in jieba.cut_for_search(text) if len(w)>=2]
    freq = {}
    for s in segs:
        freq[s] = freq.get(s,0)+1
    keys = sorted(freq.keys(), key=lambda k:(-freq[k], -len(k)))
    res = []
    for k in keys:
        if k in res: continue
        if re.match(r'^(文章|本文|示例|方法|包括|通常|可能|我们)$', k):
            continue
        res.append(k)
        if len(res)>=topn: break
    return res[:topn]

def build_summary_from_text(text):
    if not text: return '心理指南'
    # take first sentence-like chunk
    m = re.search(r'([\u4e00-\u9fa5\w\-\,\，\:]+?)[。；;\n]', text)
    if m:
        sent = m.group(1).strip()
    else:
        sent = text.strip()[:24]
    # shorten
    sent = sent.replace('\n',' ').strip()
    if len(sent) > 18:
        sent = sent[:18]
    return sent

def main(limit=100):
    conn = pymysql.connect(**DB)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    # select candidates: tags contains 心理 or tags is null/empty
    cur.execute("""
    SELECT id,title,tags,category,source,LEFT(content,2000) AS content
    FROM mind_knowledge
    WHERE tags LIKE '%%心理%%' OR tags IS NULL OR tags = ''
    LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    suggestions = []
    for r in rows:
        text = (r.get('title') or '') + '\n' + (r.get('content') or '')
        if has_jieba:
            tags = jieba_extract(text, topn=2)
        else:
            tags = simple_extract(text, topn=2)
        # ensure tags are clean
        tags = [t.replace('#','').strip() for t in tags if t and len(t.strip())>0]
        # fallback if still empty
        if not tags:
            tags = ['心理']
        # build summary: prefer existing category if meaningful
        summary = r.get('category')
        if not summary or summary.strip()=='' or summary.strip().lower()=='心理':
            summary = build_summary_from_text(text)
        suggestions.append(dict(id=r['id'], title=r['title'], old_tags=r.get('tags'), suggested_tags=tags, old_category=r.get('category'), suggested_category=summary))

    # write SQL file
    os.makedirs(os.path.dirname(OUT_SQL), exist_ok=True)
    with open(OUT_SQL, 'w', encoding='utf-8') as f:
        f.write('-- Generated update statements for mind_knowledge tags/category\n')
        f.write('-- Review before executing. This file does NOT run automatically.\n\n')
        for s in suggestions:
            tags_json = json.dumps(s['suggested_tags'], ensure_ascii=False)
            # escape single quotes in category
            cat = s['suggested_category'].replace("'","\\'")
            f.write("-- ID: {}\n".format(s['id']))
            f.write("-- Title: {}\n".format(s['title']))
            f.write("-- Old tags: {}  Old category: {}\n".format(s['old_tags'], s['old_category']))
            f.write("UPDATE mind_knowledge SET tags = '{}' , category = '{}' WHERE id = '{}';\n\n".format(tags_json, cat, s['id']))

    # print preview
    for s in suggestions:
        print('ID:', s['id'])
        print('Title:', s['title'])
        print('Old tags:', s['old_tags'])
        print('Suggested tags:', s['suggested_tags'])
        print('Old category:', s['old_category'])
        print('Suggested category:', s['suggested_category'])
        print('-'*40)

    print('\nWrote suggestions to', OUT_SQL)

if __name__ == '__main__':
    main()
