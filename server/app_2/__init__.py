# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2025 by Mood Bakery Team.
    :license: Apache 2.0, see LICENSE for more details.
"""
import atexit
import datetime
import logging
import os
import platform
from logging.handlers import TimedRotatingFileHandler

# Windows系统不支持fcntl模块
if platform.system() != 'Windows':
    import fcntl

from dotenv import load_dotenv
from flask import Flask, request, g
from flask_apscheduler import APScheduler
from flask_cors import CORS
from flask_migrate import Migrate
from flask_socketio import SocketIO
from redis import StrictRedis
from werkzeug.exceptions import HTTPException

from .lib.exception import APIException, ServerError, HeaderInvalid, AuthorizationInvalid, TokenInvalid
from .lib.token import auth, verify_token
from .model.base import db
from .patch.encoder import JSONEncoder

migrate = Migrate(db=db, render_as_batch=True, compare_type=True, compare_server_default=True)
cors = CORS(resources={'/*': {'origins': '*'}})
# 将 engine.io 的 path 设置为 '/ws'，以匹配前端 `july_client/config/api.js` 中使用的 ws 路径前缀（ws://host:port/ws）。
socketio = SocketIO(cors_allowed_origins='*', path='/ws')
scheduler = APScheduler()

# 存放微信令牌
access_token_db: StrictRedis


def create_app():
    """
    创建应用
    """
    # 载入环境变量
    load_dotenv()
    app = Flask(__name__)

    register_config(app)
    register_logging(app)
    register_extension(app)
    register_socket(app)
    register_scheduler(app)
    register_redis(app)
    register_header(app)
    register_exception(app)
    register_encoder(app)
    register_resource(app)

    return app


def register_config(app):
    """
    注册配置
    """
    flask_env = app.config.get('ENV')
    app.config.from_object(f"app.config.{flask_env}.{flask_env.capitalize()}Config")
    # 立刻打印到 stdout，确保在日志 handler 注册前也能看到（便于调试 .env / 配置）
    try:
        print(f"[config] ENV={flask_env}, SQLALCHEMY_DATABASE_URI={app.config.get('SQLALCHEMY_DATABASE_URI')}")
    except Exception:
        print('[config] failed to print SQLALCHEMY_DATABASE_URI')
    # 记录当前使用的数据库 URI，便于诊断（比如 .env 未被正确加载时会回退到 sqlite）
    try:
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        app.logger.info(f"Using SQLALCHEMY_DATABASE_URI={db_uri}")
        # 如果是 sqlite，某些 pool 参数对 sqlite 的 NullPool/SingletonThread 不适用，移除以避免 create_engine 报错
        if isinstance(db_uri, str) and db_uri.startswith('sqlite'):
            eo = app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {}) or {}
            # 仅移除不兼容的键
            for k in ('pool_size', 'max_overflow', 'pool_timeout', 'pool_recycle'):
                if k in eo:
                    eo.pop(k, None)
            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = eo
            app.logger.warning('Detected sqlite DB URI -- removed incompatible SQLALCHEMY_ENGINE_OPTIONS keys')
    except Exception:
        # 记录但不阻塞启动
        app.logger.exception('Failed to inspect/sanitize SQLALCHEMY_DATABASE_URI')
    # 优先使用环境变量中的 SQLALCHEMY_DATABASE_URI（如果用户在 .env 或系统环境中明确指定了）
    try:
        env_db = os.getenv('SQLALCHEMY_DATABASE_URI')
        if env_db and env_db.strip():
            # 如果环境变量指向 mysql，则覆盖配置，确保后端实际使用 MySQL
            app.config['SQLALCHEMY_DATABASE_URI'] = env_db.strip()
            app.logger.info(f"Overrode SQLALCHEMY_DATABASE_URI from environment: {env_db}")
        else:
            # 如果环境变量没有被 load_dotenv 正确设置，从项目根目录的 .env 手动解析一遍（容忍空格或引号）
            try:
                env_path = os.path.join(os.getcwd(), '.env')
                if os.path.exists(env_path):
                    with open(env_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip().startswith('SQLALCHEMY_DATABASE_URI'):
                                k, _, v = line.partition('=')
                                candidate = v.strip().strip('"').strip("'")
                                if candidate:
                                    app.config['SQLALCHEMY_DATABASE_URI'] = candidate
                                    app.logger.info(f"Overrode SQLALCHEMY_DATABASE_URI from .env file: {candidate}")
                                    break
            except Exception:
                app.logger.exception('Failed to read SQLALCHEMY_DATABASE_URI from .env file')
    except Exception:
        app.logger.exception('Failed to override SQLALCHEMY_DATABASE_URI from environment')


def register_logging(app):
    """
    注册日志
    """

    log_file = os.path.join('log', f"app-{datetime.date.today().strftime('%Y%m%d')}.log")
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s')
    handler = TimedRotatingFileHandler(log_file, when='midnight', backupCount=90, encoding='UTF-8')
    handler.setFormatter(formatter)
    handler.setLevel(app.config['LOG_LEVEL'])
    app.logger.addHandler(handler)

    @app.before_first_request
    def prod_logging():
        if not app.debug:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            app.logger.addHandler(stream_handler)
            app.logger.setLevel(app.config['LOG_LEVEL'])


def register_extension(app):
    """
    注册扩展
    """
    db.init_app(app)
    migrate.init_app(app)
    cors.init_app(app)


def register_socket(app):
    """
    注册 Socket
    """
    socketio.init_app(app)


def register_scheduler(app):
    """
    注册 Scheduler
    """
    scheduler.init_app(app)

    if app.debug and not scheduler.running:
        scheduler.start()

    # Windows系统不支持文件锁，直接启动scheduler
    if platform.system() == 'Windows':
        scheduler.start()
    else:
        # Unix/Linux系统使用文件锁
        f = open('scheduler.lock', 'wb')
        # noinspection PyBroadException
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            scheduler.start()
        except:
            pass

        def unlock():
            fcntl.flock(f, fcntl.LOCK_UN)
            f.close()

        atexit.register(unlock)


def register_redis(app):
    """
    注册 Redis
    """
    global access_token_db

    redis_config = {
        'host': app.config['REDIS_HOST'],
        'port': app.config['REDIS_PORT'],
        'password': app.config['REDIS_PASSWORD'],
        'decode_responses': True,
        'health_check_interval': 30
    }
    access_token_db = StrictRedis(**redis_config, db=app.config['REDIS_ACCESS_TOKEN_DB'])


def register_header(app):
    """
    注册请求头
    """

    @app.before_request
    def app_name_validator():
        if 'APP_NAME' not in app.config:
            return
        if request.path in app.config['ALLOWED_PATH'] or '*' in app.config['ALLOWED_PATH']:
            return
        if 'X-App-Name' not in request.headers or request.headers['X-App-Name'] != app.config['APP_NAME']:
            raise HeaderInvalid

    @app.before_request
    def authorization_validator():
        g.user = None
        if 'Authorization' not in request.headers:
            return
        try:
            scheme, token = request.headers.get('Authorization', '').split(None, 1)
        except ValueError:
            raise AuthorizationInvalid
        if scheme != auth.scheme:
            raise TokenInvalid
        verify_token(token=token)


def register_exception(app):
    """
    注册全局异常
    """

    @app.errorhandler(Exception)
    def handle_error(e):
        if isinstance(e, APIException):
            return e
        elif isinstance(e, HTTPException):
            return APIException(code=e.code, msg_code=e.code, msg=e.name)
        else:
            app.logger.error({
                'error': e,
                'path': request.path,
                'args': request.args.to_dict(),
                'data': request.get_json(silent=True)
            })
            if not app.debug:
                return ServerError()
            raise e


def register_encoder(app):
    """
    注册编码器
    """
    app.json_encoder = JSONEncoder


def register_resource(app):
    """
    注册资源
    """
    from .api.v2 import create_v2
    # debug route for cloud-side LBS test
    from .api.debug_lbs import bp as debug_bp

    app.register_blueprint(create_v2(), url_prefix='/v2')
    app.register_blueprint(debug_bp, url_prefix='/debug')
