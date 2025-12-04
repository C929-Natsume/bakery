import pymysql
import sys

cfg = dict(host='127.0.0.1', user='root', password='lyy20041218', db='july', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

def main():
    try:
        conn = pymysql.connect(**cfg)
    except Exception as e:
        print('连接数据库失败：', repr(e))
        sys.exit(2)

    with conn:
        cur = conn.cursor()
        try:
            cur.execute("SELECT id,title,LEFT(content,200) AS content_preview,create_time,source FROM mind_knowledge ORDER BY create_time DESC LIMIT 20;")
            rows = cur.fetchall()
            if not rows:
                print('未返回记录（表不存在或为空）。')
                return
            for r in rows:
                print('ID:', r.get('id'))
                print('创建:', r.get('create_time'))
                print('标题:', r.get('title'))
                preview = r.get('content_preview') or ''
                print('内容预览:')
                print(preview)
                print('-'*40)
        except Exception as e:
            print('查询失败：', repr(e))

if __name__ == '__main__':
    main()
