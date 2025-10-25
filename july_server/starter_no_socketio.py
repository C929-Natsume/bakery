# -*- coding: utf-8 -*-
"""
    临时启动文件（禁用SocketIO）
    用于解决SSL DLL错误
    :copyright: (c) 2023 by Jeffrey.
    :license: Apache 2.0, see LICENSE for more details.
"""
import sys
import os

# 临时禁用SocketIO导入
os.environ['DISABLE_SOCKETIO'] = '1'

from flask import Flask
from app.config.base import BaseConfig
from app.lib.exception import APIException
from app.lib.red_print import RedPrint

def create_app_simple():
    """创建简化版Flask应用（不包含SocketIO）"""
    app = Flask(__name__)
    app.config.from_object(BaseConfig)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册异常处理
    register_exception(app)
    
    return app

def register_blueprints(app):
    """注册所有API蓝图"""
    from app.api.v2 import create_blueprint_v2
    app.register_blueprint(create_blueprint_v2(), url_prefix='/v2')

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
    print('=' * 60)
    print('  启动简化版服务器（禁用SocketIO）')
    print('  服务地址: http://127.0.0.1:5000')
    print('  注意: 聊天室功能不可用')
    print('=' * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)

