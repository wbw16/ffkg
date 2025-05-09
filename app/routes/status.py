from flask import Blueprint, render_template, jsonify, current_app
from datetime import datetime, timedelta
import pymysql
from neo4j import GraphDatabase
import redis
import platform
import flask
import psutil
import time
import socket
import os

status_bp = Blueprint('status', __name__)


def get_server_ip():
    """获取服务器IP地址"""
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except:
        return "127.0.0.1"


def check_database_status():
    """检查数据库状态"""
    try:
        config = current_app.config
        conn = pymysql.connect(
            host=config['DB_HOST'],
            port=config['DB_PORT'],
            user=config['DB_USER'],
            password=config['DB_PASSWORD'],
            database=config['DB_NAME']
        )
        with conn.cursor() as cursor:
            cursor.execute("SHOW STATUS LIKE 'Uptime'")
            uptime = cursor.fetchone()[1]
            cursor.execute("SHOW VARIABLES LIKE 'version'")
            version = cursor.fetchone()[1]
        conn.close()
        return {
            'status': '运行中',
            'uptime': int(uptime),
            'version': version,
            'healthy': True
        }
    except Exception as e:
        return {
            'status': '异常',
            'error': str(e),
            'healthy': False
        }


def check_redis_status():
    """检查Redis状态"""
    try:
        config = current_app.config
        r = redis.Redis(
            host=config['REDIS_HOST'],
            port=config['REDIS_PORT'],
            db=config['REDIS_DB'],
            password=config['REDIS_PASSWORD'] or None
        )
        info = r.info()
        return {
            'status': '运行中',
            'version': info['redis_version'],
            'uptime': info['uptime_in_seconds'],
            'memory_used': info['used_memory_rss'],
            'healthy': True
        }
    except Exception as e:
        return {
            'status': '异常',
            'error': str(e),
            'healthy': False
        }


def check_neo4j_status():
    """检查Neo4j状态"""
    try:
        config = current_app.config
        driver = GraphDatabase.driver(
            config['NEO4J_URI'],
            auth=config['NEO4J_AUTH']
        )
        with driver.session() as session:
            result = session.run("CALL dbms.components() YIELD name, versions RETURN name, versions[0] as version")
            info = result.single()
        return {
            'status': '运行中',
            'version': f"{info['name']} {info['version']}",
            'healthy': True
        }
    except Exception as e:
        return {
            'status': '异常',
            'error': str(e),
            'healthy': False
        }


def get_recent_events(limit=5):
    """获取最近事件（示例）"""
    return [
        {"time": datetime.now().isoformat(), "event": "系统启动", "level": "info"},
        {"time": (datetime.now() - timedelta(minutes=30)).isoformat(), "event": "数据库备份完成", "level": "info"},
        {"time": (datetime.now() - timedelta(hours=1)).isoformat(), "event": "新用户注册", "level": "info"}
    ]


def get_disk_usage():
    """获取磁盘使用情况"""
    partitions = []
    for part in psutil.disk_partitions():
        usage = psutil.disk_usage(part.mountpoint)
        partitions.append({
            'device': part.device,
            'mountpoint': part.mountpoint,
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
            'percent': usage.percent
        })
    return partitions


@status_bp.route('/status')
def status_page():
    """状态监控页面"""
    services = {
        'MySQL': check_database_status(),
        'Neo4j': check_neo4j_status(),
        'Redis': check_redis_status()
    }

    system_info = {
        'now': datetime.now(),
        'python_version': platform.python_version(),
        'flask_version': flask.__version__,
        'environment': current_app.config.get('ENV', 'production'),
        'os': f"{platform.system()} {platform.release()}",
        'hostname': platform.node(),
        'ip_address': get_server_ip()
    }

    # 获取内存信息并正确转换
    memory = psutil.virtual_memory()
    GB = 1024 ** 3  # 1GB = 1073741824 bytes

    resource_usage = {
        'cpu': psutil.cpu_percent(interval=1),
        'memory': memory.percent,
        'memory_total_gb': round(memory.total / GB, 2),
        'memory_used_gb': round(memory.used / GB, 2),
        'memory_available_gb': round(memory.available / GB, 2),
        'memory_total_bytes': memory.total,
        'memory_used_bytes': memory.used,
        'memory_available_bytes': memory.available,
        'disk': get_disk_usage(),
        'uptime': int(time.time() - psutil.boot_time())
    }

    return render_template('status.html',
                           services=services,
                           system_info=system_info,
                           resource_usage=resource_usage,
                           events=get_recent_events())


@status_bp.route('/api/status')
def api_status():
    """API接口返回JSON格式状态"""
    try:
        system_info = {
            'python_version': platform.python_version(),
            'flask_version': flask.__version__,
            'os': f"{platform.system()} {platform.release()}",
            'hostname': platform.node(),
            'ip_address': get_server_ip()
        }

        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        resource_usage = {
            'cpu': {
                'percent': cpu,
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True)
            },
            'memory': {
                'percent': memory.percent,
                'used': memory.used,
                'total': memory.total,
                'free': memory.free
            },
            'disk': get_disk_usage(),
            'uptime': int(time.time() - psutil.boot_time()),
            'server_time': datetime.utcnow().isoformat()
        }

        services_status = {
            'database': check_database_status(),
            'redis': check_redis_status(),
            'neo4j': check_neo4j_status()
        }

        return jsonify({
            'status': 'success',
            'data': {
                'system': system_info,
                'resources': resource_usage,
                'services': services_status,
                'events': get_recent_events()
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
