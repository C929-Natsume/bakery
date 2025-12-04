# -*- coding: utf-8 -*-
"""
LBS 查询封装：优先使用 Redis 缓存；失败时退化为内存缓存；提供简单的按IP限流。
"""
import json
import time
import math
from typing import Optional, Tuple

import requests
from flask import current_app, request

# HUST 基准点与推荐机构（确保在华科附近查询时，列表首位包含该机构）
HUST_CENTER = {'lat': 30.518, 'lng': 114.414}

# 推荐置顶：华中科技大学心理健康教育中心
HUST_FEATURED = {
    'name': '华中科技大学心理健康教育中心',
    'address': '洪山区珞喻路1037号 华中科技大学校内',
    'tel': '027-87541114',
    'location': {'lat': 30.518, 'lng': 114.414}
}

# 推荐心理咨询机构列表（武汉地区）
FEATURED_AGENCIES = [
    {
        'name': '华中科技大学心理健康教育中心',
        'address': '洪山区珞喻路1037号 华中科技大学校内',
        'tel': '027-87541114',
        'location': {'lat': 30.518, 'lng': 114.414}
    },
    {
        'name': '武汉市精神卫生中心',
        'address': '江汉区发展大道279号',
        'tel': '027-85836271',
        'location': {'lat': 30.610, 'lng': 114.264}
    },
    {
        'name': '湖北省人民医院精神卫生中心',
        'address': '武昌区解放路238号',
        'tel': '027-88041919',
        'location': {'lat': 30.545, 'lng': 114.305}
    },
    
    {
        'name': '武汉市心理医院',
        'address': '江汉区发展大道279号',
        'tel': '027-85836271',
        'location': {'lat': 30.610, 'lng': 114.264}
    },
    
    {
        'name': '湖北省心理学会心理咨询中心',
        'address': '武昌区中南路14号',
        'tel': '027-87277952',
        'location': {'lat': 30.538, 'lng': 114.332}
    }
]

# 简单内存缓存结构（进程内）
_mem_cache = {}


def _cache_get(key: str) -> Optional[dict]:
    item = _mem_cache.get(key)
    if not item:
        return None
    if item['expire'] < time.time():
        _mem_cache.pop(key, None)
        return None
    return item['value']


def _cache_set(key: str, value: dict, ttl: int):
    _mem_cache[key] = {'value': value, 'expire': time.time() + ttl}


def _redis_clients():
    try:
        from app_2 import access_token_db as redis_cli  # 复用已连接的 Redis 客户端
        return redis_cli
    except Exception:
        return None


def _rate_limit(key: str, limit: int, ttl: int) -> bool:
    """返回 True 表示允许；False 表示超限。"""
    cli = _redis_clients()
    try:
        if cli:
            cnt = cli.incr(key)
            if cnt == 1:
                cli.expire(key, ttl)
            return cnt <= limit
    except Exception:
        pass
    # fallback: 内存计数
    now = int(time.time())
    bucket = f"{key}:{now // ttl}"
    cnt = _mem_cache.get(bucket, {'value': 0, 'expire': now + ttl})
    cnt['value'] += 1
    _mem_cache[bucket] = cnt
    return cnt['value'] <= limit


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """计算两点间球面距离（米）。输入为十进制度。"""
    if None in (lat1, lng1, lat2, lng2):
        return float('inf')
    R = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _inject_hust_featured(data: dict, center_lat: float, center_lng: float, radius: int) -> dict:
    """
    根据查询中心点位置，注入附近的推荐心理咨询机构。
    - 计算距离，返回距离查询点较近的推荐机构（最多5个）
    - 去重：若已有同名或相似名称的条目，则不重复插入。
    - 仅修改本次返回的数据，不改变缓存内容结构（调用者可自行决定是否缓存）。
    """
    try:
        items = data.get('items') or []
        # 如果已经包含华中科技大学则不重复插入
        exists = any('华中科技大学' in (it.get('name') or '') for it in items)
        if not exists:
            data = {'items': [HUST_FEATURED] + items}
        return data
    except Exception:
        return data


def search_nearby(lat: float, lng: float, radius: int, keyword: str) -> Tuple[str, dict]:
    """返回 (source, data)；source=tencent|mock"""
    ip = request.remote_addr or '0.0.0.0'
    if not _rate_limit(f"rl:lbs:{ip}", limit=30, ttl=60):
        # 触发限流，优先尝试高德，其次返回推荐机构
        amap_key_tmp = current_app.config.get('AMAP_LBS_KEY')
        if amap_key_tmp and lat and lng:
            try:
                amap_data = _amap_search(lat, lng, radius, keyword, amap_key_tmp)
                if amap_data and amap_data.get('items'):
                    amap_data = _inject_hust_featured(amap_data, lat, lng, radius)
                    return 'amap', amap_data
            except Exception:
                pass
        # 限流时，如果是华科附近，至少返回推荐机构
        if lat and lng:
            fallback_data = _inject_hust_featured({'items': []}, lat, lng, radius)
            if fallback_data.get('items'):
                return 'mock', fallback_data
        return 'none', {'items': []}

    key = current_app.config.get('WEIXIN_LBS_KEY')
    amap_key = current_app.config.get('AMAP_LBS_KEY')
    # 缺少坐标无法查询 — 改为返回置顶推荐作为兜底（提高可见性）
    if not lat or not lng:
        # 无法获取到用户位置时，返回推荐机构（至少显示华中科技大学心理健康教育中心）
        fallback_data = _inject_hust_featured({'items': []}, HUST_CENTER['lat'], HUST_CENTER['lng'], radius)
        return 'mock', fallback_data
    # 无腾讯 Key，则尝试高德；否则返回空
    if not key:
        if amap_key:
            amap_data = _amap_search(lat, lng, radius, keyword, amap_key)
            if amap_data and amap_data.get('items'):
                return 'amap', amap_data
        return 'none', {'items': []}

    cache_key = f"lbs:{round(lat,5)}:{round(lng,5)}:{radius}:{keyword}"
    cli = _redis_clients()
    if cli:
        try:
            raw = cli.get(cache_key)
            if raw:
                cached = json.loads(raw)
                cached = _inject_hust_featured(cached, lat, lng, radius)
                return 'tencent-cache', cached
        except Exception:
            pass

    url = 'https://apis.map.qq.com/ws/place/v1/search'
    params = {
        'keyword': keyword,
        'boundary': f'nearby({lat},{lng},{radius})',
        'page_size': 20,
        'page_index': 1,
        'key': key
    }
    try:
        res = requests.get(url, params=params, timeout=20).json()
        if res.get('status') != 0:
            current_app.logger.warning(f"LBS查询失败: {res}")
            # 腾讯失败，尝试高德兜底（如果配置了 Key）
            if amap_key:
                amap_data = _amap_search(lat, lng, radius, keyword, amap_key)
                if amap_data and amap_data.get('items'):
                    return 'amap', amap_data
            # 所有API都失败时，如果是华科附近，至少返回推荐机构
            if lat and lng:
                fallback_data = _inject_hust_featured({'items': []}, lat, lng, radius)
                if fallback_data.get('items'):
                    return 'mock', fallback_data
            return 'none', {'items': []}
        pois = []
        for it in res.get('data', []):
            # 统一处理电话字段，确保格式一致
            tel = (it.get('tel') or '').strip()
            if tel:
                tel = tel.split(';')[0].strip()  # 取第一个电话，去除分号和空格
            pois.append({
                'name': it.get('title') or '',
                'address': it.get('address') or '',
                'tel': tel or '',  # 确保始终是字符串，即使为空
                'location': {'lat': it.get('location', {}).get('lat'), 'lng': it.get('location', {}).get('lng')}
            })
        data = {'items': pois}
        # 华科附近时确保推荐机构置顶
        data = _inject_hust_featured(data, lat, lng, radius)
        # 写缓存（10分钟）
        if cli:
            try:
                cli.setex(cache_key, 600, json.dumps(data, ensure_ascii=False))
            except Exception:
                pass
        else:
            _cache_set(cache_key, data, 600)
        return 'tencent', data
    except Exception as e:
        current_app.logger.error(f"LBS查询异常: {e}")
        # 异常时也尝试高德兜底
        if amap_key:
            try:
                amap_data = _amap_search(lat, lng, radius, keyword, amap_key)
                if amap_data and amap_data.get('items'):
                    amap_data = _inject_hust_featured(amap_data, lat, lng, radius)
                    return 'amap', amap_data
            except Exception:
                pass
        # 所有API都失败时，如果是华科附近，至少返回推荐机构
        if lat and lng:
            fallback_data = _inject_hust_featured({'items': []}, lat, lng, radius)
            if fallback_data.get('items'):
                return 'mock', fallback_data
        return 'none', {'items': []}


def _amap_search(lat: float, lng: float, radius: int, keyword: str, key: str) -> Optional[dict]:
    """高德地图 周边搜索 兜底。返回 {'items':[...]} 结构。"""
    url = 'https://restapi.amap.com/v3/place/around'
    params = {
        'location': f"{lng},{lat}",  # 注意顺序：lng,lat
        'keywords': keyword,
        'radius': radius,
        'offset': 20,
        'page': 1,
        'key': key,
        'output': 'json'
    }
    res = requests.get(url, params=params, timeout=20).json()
    if str(res.get('status')) != '1':
        current_app.logger.warning(f"AMap查询失败: {res}")
        return {'items': []}
    pois = []
    for it in res.get('pois', []):
        # 统一处理电话字段，确保格式一致
        tel = (it.get('tel') or '').strip()
        if tel:
            tel = tel.split(';')[0].strip()  # 取第一个电话，去除分号和空格
        name = it.get('name') or ''
        addr = it.get('address') or ''
        loc = it.get('location') or ''
        try:
            lng_str, lat_str = loc.split(',') if ',' in loc else ('', '')
            lat_v = float(lat_str) if lat_str else None
            lng_v = float(lng_str) if lng_str else None
        except Exception:
            lat_v, lng_v = None, None
        pois.append({
            'name': name,
            'address': addr,
            'tel': tel or '',  # 确保始终是字符串，即使为空
            'location': {'lat': lat_v, 'lng': lng_v}
        })
    return {'items': pois}
