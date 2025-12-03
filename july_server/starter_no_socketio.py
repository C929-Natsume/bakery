# -*- coding: utf-8 -*-
"""
    启动文件（使用完整Flask应用但不启动SocketIO服务器）
    用于云托管部署或避免SSL DLL错误
    :copyright: (c) 2023 by Jeffrey.
    :license: Apache 2.0, see LICENSE for more details.
"""
from app import create_app

# 创建完整的Flask应用（包含所有功能）
app = create_app()

# SocketIO已初始化但不会启动服务器，聊天功能不可用
# 所有REST API功能正常

if __name__ == '__main__':
    print('=' * 60)
    print('  启动服务器（REST API模式）')
    print('  服务地址: http://0.0.0.0:5000')
    print('  注意: 聊天室功能不可用')
    print('=' * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)

