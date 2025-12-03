import os
import traceback

URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'mysql+cymysql://root:cqh050708@127.0.0.1:3306/july?charset=utf8mb4'

def parse_uri(uri):
    # expected format: mysql+cymysql://user:pass@host:port/db?charset=...
    try:
        from urllib.parse import urlparse, parse_qs
        p = urlparse(uri)
        user = p.username
        password = p.password
        host = p.hostname
        port = p.port or 3306
        db = p.path.lstrip('/')
        qs = parse_qs(p.query)
        return dict(user=user, password=password, host=host, port=port, db=db, qs=qs)
    except Exception:
        return None


def try_connect(cfg):
    print('Attempting DB connect with:', cfg)
    try:
        # try cymysql first
        try:
            import cymysql as dbdriver
            # try a few call styles to adapt to installed cymysql variant
            try:
                conn = dbdriver.connect(cfg['host'], cfg['user'], cfg['password'], cfg['db'], cfg['port'])
            except Exception:
                try:
                    conn = dbdriver.connect(host=cfg['host'], user=cfg['user'], passwd=cfg['password'], database=cfg['db'], port=cfg['port'])
                except Exception:
                    conn = dbdriver.connect(host=cfg['host'], user=cfg['user'], password=cfg['password'], database=cfg['db'], port=cfg['port'])
            print('Connected using cymysql, server version:', conn.get_server_info())
            conn.close()
            return True
        except Exception as e:
            print('cymysql connection failed:', e)
        # fallback to pymysql
        try:
            import pymysql as dbdriver
            conn = dbdriver.connect(host=cfg['host'], user=cfg['user'], password=cfg['password'], db=cfg['db'], port=cfg['port'])
            print('Connected using pymysql, server version:', conn.get_server_info())
            conn.close()
            return True
        except Exception as e:
            print('pymysql connection failed:', e)
            traceback.print_exc()
            return False
    except Exception:
        traceback.print_exc()
        return False


if __name__ == '__main__':
    cfg = parse_uri(URI)
    if not cfg:
        print('Failed to parse URI:', URI)
    else:
        ok = try_connect(cfg)
        print('OK' if ok else 'FAILED')
