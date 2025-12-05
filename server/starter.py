# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2025 by Mood Bakery Team.
    :license: Apache 2.0, see LICENSE for more details.
"""
import os
from dotenv import load_dotenv
from app_2 import create_app, socketio

"""
启动方式：读取 .env 中的 APP_HOST、APP_PORT、APP_RELOAD；
默认保持兼容：host=0.0.0.0, port=5000, debug=True。
"""

# 确保环境变量载入（create_app 里也会载入，这里再次调用以便最早取到端口）
load_dotenv()

app = create_app()

if __name__ == '__main__':
    host = os.getenv('APP_HOST', '0.0.0.0')
    port = int(os.getenv('APP_PORT', '5000'))
    debug = os.getenv('APP_RELOAD', 'true').lower() in ('1', 'true', 'yes', 'on')
    socketio.run(app, host=host, port=port, debug=debug)

