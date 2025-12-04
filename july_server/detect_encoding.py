from pathlib import Path
p=Path("sql/mind_seed.generated.sql")
b=p.read_bytes()
encs=["utf-8","utf-8-sig","gbk","cp936","latin1","utf-16"]
for enc in encs:
    try:
        s=b.decode(enc)
        print("=== decode as",enc,"OK ===")
        print(s[:800].replace("\n","\\n"))
        print()
    except Exception as e:
        print("=== decode as",enc,"FAILED:",e)
        print()
