# -*- coding: utf-8 -*-
"""
convert_sql_to_utf8.py
尝试用常见编码读取一个 SQL 文件（utf-8, utf-8-sig, gbk, latin1），并写成 UTF-8 无 BOM 输出文件。
用法:
    python convert_sql_to_utf8.py path\to\mind_seed.generated.sql path\to\mind_seed.utf8.sql

在 Windows 上请用 cmd 或 PowerShell 调用 python（建议 cmd）。
"""
import sys
from pathlib import Path

candidates = ["utf-8", "utf-8-sig", "gbk", "latin1"]

def detect_and_convert(src: Path, dst: Path):
    if not src.exists():
        print(f"源文件不存在: {src}")
        return 2
    data = None
    used = None
    for enc in candidates:
        try:
            with src.open("r", encoding=enc, errors="strict") as f:
                data = f.read()
            used = enc
            break
        except Exception as e:
            # 尝试下一个编码
            continue
    if data is None:
        # 最后用 latin1 强行读取（不会抛）
        with src.open("r", encoding="latin1", errors="replace") as f:
            data = f.read()
        used = "latin1 (fallback, replaced invalid bytes)"

    # 清理常见 Windows CRLF -> 保持 CRLF 不强制更改，但去除 BOM（utf-8-sig 已处理）
    # 写为 UTF-8 无 BOM
    with dst.open("w", encoding="utf-8", newline="\n") as f:
        f.write(data)

    print("转换完成:")
    print(f"  源: {src}")
    print(f"  目标: {dst}")
    print(f"  采用解码: {used}")
    return 0

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("用法: python convert_sql_to_utf8.py 源.sql 目标.utf8.sql")
        sys.exit(1)
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    rc = detect_and_convert(src, dst)
    sys.exit(rc)
