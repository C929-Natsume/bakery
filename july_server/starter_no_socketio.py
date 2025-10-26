# -*- coding: utf-8 -*-
"""
    临时启动文件（禁用SocketIO）
    用于解决SSL DLL错误
    :copyright: (c) 2023 by Jeffrey.
    :license: Apache 2.0, see LICENSE for more details.
"""
import sys
import os
from dotenv import load_dotenv

# 临时禁用SocketIO导入
os.environ['DISABLE_SOCKETIO'] = '1'

from flask import Flask
from flask_cors import CORS
from app.model.base import db
from app.patch.encoder import JSONEncoder
from app.config.base import BaseConfig
from app.lib.exception import APIException
from app.lib.red_print import RedPrint

def create_app_simple():
    """创建简化版Flask应用（不包含SocketIO）"""
    # 载入环境变量，便于读取 APP_HOST/APP_PORT 等
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(BaseConfig)
    # 关键：注册 SQLAlchemy 等最小必要扩展
    db.init_app(app)
    CORS(app, resources={'/*': {'origins': '*'}})
    app.json_encoder = JSONEncoder
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册异常处理
    register_exception(app)
    
    return app

def register_blueprints(app):
    """注册所有API蓝图"""
    # 实际项目中提供的是 create_v2
    from app.api.v2 import create_v2
    app.register_blueprint(create_v2(), url_prefix='/v2')

def register_exception(app):
    """注册异常处理"""
    @app.errorhandler(Exception)
    def framework_error(e):
        if isinstance(e, APIException):
            return e
        if isinstance(e, AssertionError):
            return APIException(msg=str(e))
        raise e

app = create_app_simple()

if __name__ == '__main__':
    host = os.getenv('APP_HOST', '0.0.0.0')
    port = int(os.getenv('APP_PORT', '5000'))
    debug = os.getenv('APP_RELOAD', 'true').lower() in ('1', 'true', 'yes', 'on')

    print('=' * 60)
    print('  启动简化版服务器（禁用SocketIO）')
    print(f'  服务地址: http://{host}:{port}')
    print('  注意: 聊天室功能不可用')
    print('=' * 60)
    app.run(debug=debug, host=host, port=port)

