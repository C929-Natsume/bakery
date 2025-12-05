# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, current_app
import requests
import time

bp = Blueprint('debug', __name__)


@bp.route('/lbs-test')
def lbs_test():
    """在云环境中请求腾讯地图（QQ 地图）并返回耗时与状态，用于排查云侧能否出网。"""
    key = current_app.config.get('WEIXIN_LBS_KEY')
    if not key:
        return jsonify({'ok': False, 'error': 'WEIXIN_LBS_KEY not configured in environment'}), 500

    url = 'https://apis.map.qq.com/ws/place/v1/search'
    params = {
        'keyword': '心理咨询',
        'boundary': 'nearby(30.518,114.414,3000)',
        'key': key
    }
    try:
        t0 = time.time()
        r = requests.get(url, params=params, timeout=10)
        elapsed = round(time.time() - t0, 3)
        safe_text = r.text[:2000] if r.text else ''
        return jsonify({
            'ok': True,
            'status_code': r.status_code,
            'elapsed_seconds': elapsed,
            'text_head': safe_text
        }), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
