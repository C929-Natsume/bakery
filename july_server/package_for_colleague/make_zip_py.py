#!/usr/bin/env python3
"""
make_zip_py.py
更稳健的打包脚本，使用 Python 标准库创建 zip，避免 PowerShell 控制台编码问题。
用法（在 juli_server 目录运行）:
  python package_for_colleague\make_zip_py.py
或指定包含 rollback:
  python package_for_colleague\make_zip_py.py --include-rollback

输出: ./july_seed_package_py.zip
"""
import argparse
import os
from pathlib import Path
import zipfile

FILES = [
    Path("sql/mind_seed.generated.sql"),
    Path("sql/update_selected_mind.sql"),
    Path("sql/update_mind_suggestions.sql"),
    Path("scripts/apply_update_suggestions.py"),
    Path("scripts/convert_sql_to_utf8.py"),
    Path("scripts/test_mysql_connect.py"),
]

ENV_CANDIDATES = [Path(".env.example"), Path("package_for_colleague/.env.example")]
ROLLBACK_GLOB = "sql/rollback_mind_records_*.sql"

def gather_files(include_rollback=False):
    base = Path.cwd()
    included = []
    missing = []
    for p in FILES:
        ap = base / p
        if ap.exists():
            included.append(ap)
        else:
            missing.append(str(p))
    # env
    for c in ENV_CANDIDATES:
        ap = base / c
        if ap.exists():
            included.append(ap)
            break
    # rollback
    if include_rollback:
        for rb in sorted(base.glob(ROLLBACK_GLOB)):
            included.append(rb)
    return included, missing


def make_zip(out_name, files):
    out = Path(out_name)
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for f in files:
            arcname = str(f.relative_to(Path.cwd()))
            z.write(f, arcname)
            print(f"Added: {arcname}")
    print(f"\nCreated zip: {out.resolve()}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--include-rollback', action='store_true', help='Include rollback SQL files if present')
    args = ap.parse_args()

    files, missing = gather_files(include_rollback=args.include_rollback)
    print('Files found to include:')
    for f in files:
        print(' -', f)
    if missing:
        print('\nMissing expected files (will not be included):')
        for m in missing:
            print(' -', m)

    if not files:
        print('\nNo files found to package. Exiting.')
        return 2

    make_zip('july_seed_package_py.zip', files)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
