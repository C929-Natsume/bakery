#!/usr/bin/env python3
"""
最小可行爬虫：Requests + BeautifulSoup（优先使用 readability 提取正文），用于非商业快速试验。
用法：
  python simple_crawler.py --urls urls.txt
或：
  python simple_crawler.py https://example.com/article1 https://example.com/article2

输出：默认写到 `./server/data/crawl_output.jsonl`（每行一个 JSON，包含 url/title/content/html）
依赖：
  pip install requests bs4 readability-lxml
  （若不安装 readability-lxml，脚本会回退到简单的段落抽取逻辑）

注意：请遵守目标站点的 robots.txt 与版权/使用条款。仅用于学习/个人用途。
"""

import argparse
import json
import os
import sys
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

try:
    # readability-lxml 提供更可靠的正文抽取（可选）
    from readability import Document
    HAVE_READABILITY = True
except Exception:
    HAVE_READABILITY = False

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36'
}

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(OUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUT_DIR, 'crawl_output.jsonl')


def fetch(url, timeout=15):
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    # 尽量以 resp.apparent_encoding 或 utf-8 解码
    resp.encoding = resp.encoding or resp.apparent_encoding or 'utf-8'
    return resp.text


def extract_with_readability(html):
    doc = Document(html)
    title = doc.short_title() or ''
    content_html = doc.summary() or ''
    # 用 bs4 进一步把段落分离
    soup = BeautifulSoup(content_html, 'lxml')
    paras = [p.get_text().strip() for p in soup.find_all(['p', 'div'])]
    paras = [p for p in paras if p]
    return title, paras, content_html


def fallback_extract(html):
    soup = BeautifulSoup(html, 'lxml')
    # title
    title_tag = soup.find('title')
    title = title_tag.get_text().strip() if title_tag else ''

    # 尝试 article 标签
    article = soup.find('article')
    if article:
        paras = [p.get_text().strip() for p in article.find_all('p') if p.get_text().strip()]
        content_html = str(article)
        if paras:
            return title, paras, content_html

    # 否则查找所有 <div> 或 <section>，选取包含最多文本长度的节点
    candidates = soup.find_all(['div', 'section'], recursive=True)
    best = None
    best_len = 0
    for c in candidates:
        text = c.get_text(separator=' ', strip=True)
        if len(text) > best_len:
            best_len = len(text)
            best = c
    if best is not None and best_len > 200:
        paras = [p.get_text().strip() for p in best.find_all('p') if p.get_text().strip()]
        if not paras:
            # 如果没有 p，则按句子/换行分割
            text = best.get_text('\n')
            paras = [line.strip() for line in text.split('\n') if len(line.strip())>30]
        content_html = str(best)
        return title, paras, content_html

    # 最后退回到页面中所有 <p> 的组合
    paras = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()]
    return title, paras, str(soup)


def process_url(url):
    try:
        html = fetch(url)
    except Exception as e:
        print(f'Fetch failed for {url}:', e)
        return None

    if HAVE_READABILITY:
        try:
            title, paras, content_html = extract_with_readability(html)
        except Exception:
            title, paras, content_html = fallback_extract(html)
    else:
        title, paras, content_html = fallback_extract(html)

    # join paras with blank line to match客户端分段逻辑
    content = '\n\n'.join(paras)
    return {
        'url': url,
        'title': title,
        'content': content,
        'html_preview': content_html[:2000]
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--urls', help='文件路径，包含每行一个 URL')
    p.add_argument('urls_args', nargs='*', help='或者在命令行传入 URL 列表')
    p.add_argument('--delay', type=float, default=1.0, help='请求间隔（秒）')
    args = p.parse_args()

    urls = []
    if args.urls:
        with open(args.urls, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    urls.append(line)
    urls.extend(args.urls_args)

    if not urls:
        print('请提供 URL 列表（文件或命令行参数）。')
        sys.exit(1)

    print(f'Starting crawl of {len(urls)} url(s). Readability available: {HAVE_READABILITY}')

    with open(OUT_FILE, 'a', encoding='utf-8') as out:
        for i, url in enumerate(urls, 1):
            print(f'[{i}/{len(urls)}] {url}')
            rec = process_url(url)
            if rec:
                out.write(json.dumps(rec, ensure_ascii=False) + '\n')
            time.sleep(args.delay)

    print('Crawl completed. Output file:', OUT_FILE)


if __name__ == '__main__':
    main()
