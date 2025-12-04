#!/usr/bin/env python3
"""
针对 wenda.xinlixue.cn 的专用抓取与解析器。
输入：一个包含 URL 列表的文件（每行一个 url），或直接在命令行传入 URL。
输出：`../data/clean_wenda.jsonl`，每行 JSON 包含: id(urlhash), url, title, content (段落以\n\n分隔), source

依赖：pip install requests beautifulsoup4 lxml

注意：本脚本会直接请求每个 URL，请在本地运行并保证网络可达。
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36'
}

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(OUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUT_DIR, 'clean_wenda.jsonl')


def fetch(url, timeout=15):
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.encoding = r.encoding or r.apparent_encoding or 'utf-8'
    return r.text


def extract_wenda(html):
    soup = BeautifulSoup(html, 'lxml')
    # 题目选择器：尽量兼容不同样式
    title_sel = ['.question-title', '.wenda-title', 'h1', '.article-title']
    title = ''
    for sel in title_sel:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            title = el.get_text(strip=True)
            break

    # 答案选择器：常见的回答容器
    answer_selectors = ['.answer-content', '.wenda-answer', '.answer-text', '.reply-content', '.content']
    answers = []
    for sel in answer_selectors:
        nodes = soup.select(sel)
        if nodes:
            for n in nodes:
                # remove scripts/styles/meta
                for bad in n.select('script, style, .meta, .actions, .like, .avatar, .time'):
                    bad.decompose()
                text = n.get_text('\n', strip=True)
                # cleanup multiple blank lines
                text = re.sub(r'\n{2,}', '\n\n', text)
                if len(text) > 30:
                    answers.append(text)
            # if we found nodes for this selector, assume it's the right one
            if answers:
                break

    # fallback: find large <div> or <article>
    if not answers:
        candidates = soup.find_all(['article', 'div'], recursive=True)
        for c in candidates:
            t = c.get_text('\n', strip=True)
            if len(t) > 200:
                # split into paragraphs and take chunks
                parts = [p.strip() for p in t.split('\n') if len(p.strip()) > 30]
                if parts:
                    answers.extend(parts[:5])
                    break

    # join answers, each answer becomes a paragraph
    content = '\n\n'.join(answers)
    return title, content


def url_hash(url):
    return hashlib.md5(url.encode('utf-8')).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--urls', help='file with urls (one per line)')
    p.add_argument('urls_args', nargs='*', help='or pass urls directly')
    p.add_argument('--delay', type=float, default=1.5)
    args = p.parse_args()

    urls = []
    if args.urls:
        with open(args.urls, 'r', encoding='utf-8') as f:
            for line in f:
                u = line.strip()
                if u:
                    urls.append(u)
    urls.extend(args.urls_args)

    if not urls:
        print('Please provide urls via file or args')
        sys.exit(1)

    print(f'Processing {len(urls)} urls to extract wenda content...')
    with open(OUT_FILE, 'w', encoding='utf-8') as out:
        for i, url in enumerate(urls, 1):
            print(f'[{i}/{len(urls)}] {url}')
            try:
                html = fetch(url)
            except Exception as e:
                print('Fetch failed:', e)
                continue
            title, content = extract_wenda(html)
            rec = {
                'id': url_hash(url),
                'url': url,
                'title': title or '',
                'content': content or '',
                'source': 'wenda.xinlixue.cn'
            }
            out.write(json.dumps(rec, ensure_ascii=False) + '\n')
            time.sleep(args.delay)

    print('Extraction completed. Results written to', OUT_FILE)


if __name__ == '__main__':
    main()
