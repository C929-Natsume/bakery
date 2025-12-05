#!/usr/bin/env python3
"""
自动发现候选文章链接脚本（requests + BeautifulSoup）
说明：
- 目标：从给定站点的若干 seed 页面抓取链接，筛选出可能的文章详情页候选（按 URL 模式与标题长度过滤），并输出到 JSONL/文本文件，供下一步人工确认。
- 特点：不处理需要 JS 渲染的站点（例如 kuakua.app 已被排除）；不使用任何 LLM。
- 输出：`../data/candidate_links.jsonl`（每行一条 JSON，包含 site, url, title, score）
- 依赖：pip install requests beautifulsoup4 lxml

用法示例：
  python link_extractor.py --sites xinli001 xinlixue csdn cnki --per-site 30
  python link_extractor.py --seeds seeds.txt --per-site 50

脚本策略简要：
- 对每个站点使用预设的 seed 路径（若提供）；抓取 seed 页面，解析所有 <a href>
- 规范化为绝对 URL；过滤掉非 http/https、包含登录/注册/下载/付费等关键词的链接
- 用简单的启发式规则对链接进行打分：URL 中包含 article/post/content/p/news 等得高分；title 长度在 30-300 的得分更高
- 去重并保留每站 top-N 候选
- 输出供你人工确认（建议你检查并筛掉付费/版权受限条目）

注意事项：
- 请先确认目标站点 robots.txt 对抓取的允许范围；本脚本没有自动遵守 robots.txt，但会尽量低速率（默认 1 秒间隔），你也可以先手工检查。
- 对 CNKI（cnki.net）：很多文章受限或需要登录/付费，建议只抓取摘要/标题用于备选，不要抓取全文。

"""

import argparse
import json
import os
import re
import sys
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36'
}

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(OUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUT_DIR, 'candidate_links.jsonl')

# 站点默认 seed 路径，基于你提供的站点。可按需扩展。
SITE_SEEDS = {
    'xinli001': [
        'https://www.xinli001.com/',
        'https://www.xinli001.com/info/101000/101005/101005-0-1-0-0-0-0-0-0-0-1.html',
        'https://www.xinli001.com/info/101000/101003/101003-0-1-0-0-0-0-0-0-0-1.html'
    ],
    'xinlixue': [
        'https://www.xinlixue.cn/',
    ],
    'csdn': [
        'https://www.csdn.net/',
        'https://blog.csdn.net/',
    ],
    'cnki': [
        'https://www.cnki.net/',
    ],
    # kuakua.app 已排除（JS 渲染）
}

# URL 或 title 中包含这些关键词则排除（登录/付费/下载/媒体等）
EXCLUDE_PATTERNS = [
    'login', 'signin', 'register', 'signup', 'pay', 'payment', 'download', 'pdf', 'subscription', 'vip', 'cart', 'order'
]

# URL 中可能表示文章详情的关键词，出现则提高得分
ARTICLE_KEYWORDS = ['article', 'news', 'post', 'content', 'p/', '/p/', '/a/', '/article/', 'detail', 'view', 'doc', 'paper', 'read']

# 主题关键词：用于优先筛选心理类文章（中文）
TOPIC_KEYWORDS = ['心理', '心理学', '情绪', '抑郁', '焦虑', '治疗', '咨询', '成长', '情感', '自我']


def fetch(url, timeout=12):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.encoding = r.encoding or r.apparent_encoding or 'utf-8'
        return r.text
    except Exception as e:
        print('Fetch failed:', url, e)
        return None


def normalize_link(href, base):
    if not href:
        return None
    href = href.strip()
    # skip anchors and mailto
    if href.startswith('#') or href.startswith('mailto:') or href.startswith('javascript:'):
        return None
    return urljoin(base, href)


def likely_article(url, title, site_key=None):
    u = url.lower()
    t = (title or '').strip()
    # exclude patterns
    for ex in EXCLUDE_PATTERNS:
        if ex in u:
            return False
        if ex in t.lower():
            return False
    # must be http(s)
    if not u.startswith('http://') and not u.startswith('https://'):
        return False
    # heuristic scoring
    score = 0
    for kw in ARTICLE_KEYWORDS:
        if kw in u:
            score += 3
    # title length
    if 20 <= len(t) <= 300:
        score += 2
    elif len(t) > 300:
        score += 1
    # path depth (too shallow like domain root is not article)
    path = urlparse(u).path
    depth = len([p for p in path.split('/') if p])
    if depth >= 2:
        score += 1
    # 如果是心理站点（例如 xinli001/xinlixue），要求标题或 URL 包含心理相关关键词
    if site_key and site_key in ('xinli001', 'xinlixue'):
        keyword_found = any(kw in u or kw in t.lower() for kw in TOPIC_KEYWORDS)
        return score >= 3 and keyword_found
    # 对其他站点，若 URL 或标题包含主题关键词也应优先保留
    if any(kw in u or kw in t.lower() for kw in TOPIC_KEYWORDS):
        score += 2

    return score >= 3


def extract_links_from_html(html, base):
    soup = BeautifulSoup(html, 'lxml')
    links = []
    for a in soup.find_all('a', href=True):
        href = a.get('href')
        full = normalize_link(href, base)
        if not full:
            continue
        title = (a.get_text() or '').strip()
        links.append((full, title))
    return links


def collect_candidates_for_site(site_key, per_site=30, delay=1.0):
    seeds = SITE_SEEDS.get(site_key, [])
    if not seeds:
        print(f'No seeds for site {site_key}, skipping')
        return []
    seen = set()
    candidates = []
    for seed in seeds:
        print('Fetching seed:', seed)
        html = fetch(seed)
        if not html:
            continue
        links = extract_links_from_html(html, seed)
        for url, title in links:
            url_norm = url.split('#')[0].rstrip('/')
            if url_norm in seen:
                continue
            seen.add(url_norm)
            if likely_article(url_norm, title, site_key=site_key):
                candidates.append({'site': site_key, 'url': url_norm, 'title': title, 'score': 0})
        time.sleep(delay)
    # dedupe by url and return top N (we don't compute score beyond heuristics)
    out = []
    for c in candidates:
        out.append(c)
        if len(out) >= per_site:
            break
    print(f'Found {len(out)} candidates for {site_key}')
    return out


def main():
    p = argparse.ArgumentParser(description='Extract candidate article links from sites')
    p.add_argument('--sites', nargs='+', help='site keys to run (e.g. xinli001 xinlixue csdn cnki)')
    p.add_argument('--seeds', help='file with seed URLs (one per line)')
    p.add_argument('--per-site', type=int, default=30, help='max candidates per site')
    p.add_argument('--delay', type=float, default=1.0, help='seconds between seed page requests')
    args = p.parse_args()

    sites = []
    if args.sites:
        sites = args.sites
    elif args.seeds:
        # read seeds file and infer site keys from hostnames
        with open(args.seeds, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if not url:
                    continue
                host = urlparse(url).hostname or url
                # attempt to map host to known keys
                if 'xinli001' in host:
                    if 'xinli001' not in sites:
                        sites.append('xinli001')
                elif 'xinlixue' in host:
                    if 'xinlixue' not in sites:
                        sites.append('xinlixue')
                elif 'cnki' in host:
                    if 'cnki' not in sites:
                        sites.append('cnki')
                elif 'csdn' in host:
                    if 'csdn' not in sites:
                        sites.append('csdn')
                # others ignored
    else:
        # default to all known except kuakua
        sites = list(SITE_SEEDS.keys())

    all_candidates = []
    for s in sites:
        if s == 'kuakua' or 'kuakua' in s:
            print('Skipping JS-rendered site kuakua (excluded)')
            continue
        cands = collect_candidates_for_site(s, per_site=args.per_site, delay=args.delay)
        all_candidates.extend(cands)

    # write results to jsonl
    with open(OUT_FILE, 'w', encoding='utf-8') as out:
        for c in all_candidates:
            out.write(json.dumps(c, ensure_ascii=False) + '\n')

    print('Done. Candidate links written to', OUT_FILE)
    print('Please review the file and remove paywalled/undesired links before next step.')


if __name__ == '__main__':
    main()
