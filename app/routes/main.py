import platform

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from app.models import (
    Basin, River, Reservoir,
    FloodControlFacility, WeatherStation, MonitoringStation,
    RiverFlowData, WaterLevelData, FloodAlert,
)
import psutil
from app.extensions import db
from datetime import datetime, timedelta
from flask import Blueprint, jsonify
from app.neo4j_models import Neo4jSync
from app.extensions import db

main_bp= Blueprint('main', __name__)
# ==================== 主路由 ====================
@main_bp.route('/')
def index():
    # 获取各类数据统计
    stats = {
        'basin_count': Basin.query.count(),
        'river_count': River.query.count(),
        'reservoir_count': Reservoir.query.count(),
        'station_count': WeatherStation.query.count(),
        'facility_count': FloodControlFacility.query.count(),
        'monitor_count': MonitoringStation.query.count()
    }

    # 获取最近添加的数据（假设模型中有created_at字段）
    recent_data = {
        'recent_basins': Basin.query.order_by(Basin.created_at.desc()).limit(5).all(),
        'recent_monitors': MonitoringStation.query.order_by(MonitoringStation.created_at.desc()).limit(5).all()
    }

    return render_template('index.html', **stats, **recent_data)
@main_bp.route('/api/sync-neo4j', methods=['POST'])
def sync_neo4j():
    """HTTP接口版的数据同步到Neo4j"""
    try:
        # 调用同步方法
        Neo4jSync.sync_all()
        return jsonify({
            'status': 'success',
            'message': '数据同步到Neo4j完成'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'同步失败: {str(e)}'
        }), 500

def get_system_info():
    # 获取CPU信息
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count(logical=False)
    cpu_count_logical = psutil.cpu_count(logical=True)

    # 获取内存信息
    mem = psutil.virtual_memory()
    mem_total = round(mem.total / (1024 ** 3), 2)
    mem_used = round(mem.used / (1024 ** 3), 2)
    mem_percent = mem.percent

    # 获取磁盘信息
    disk = psutil.disk_usage('/')
    disk_total = round(disk.total / (1024 ** 3), 2)
    disk_used = round(disk.used / (1024 ** 3), 2)
    disk_percent = disk.percent

    # 获取网络信息
    net_io = psutil.net_io_counters()
    net_sent = round(net_io.bytes_sent / (1024 ** 2), 2)
    net_recv = round(net_io.bytes_recv / (1024 ** 2), 2)

    # 获取系统信息
    boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    system_info = {
        'system': platform.system(),
        'node': platform.node(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor()
    }

    # 获取进程信息
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
        processes.append({
            'pid': proc.info['pid'],
            'name': proc.info['name'],
            'username': proc.info['username'],
            'cpu_percent': round(proc.info['cpu_percent'], 1),
            'memory_percent': round(proc.info['memory_percent'], 1)
        })

    # 按CPU使用率排序进程
    processes = sorted(processes, key=lambda p: p['cpu_percent'], reverse=True)[:10]

    return {
        'cpu': {
            'percent': cpu_percent,
            'count': cpu_count,
            'count_logical': cpu_count_logical
        },
        'memory': {
            'total': mem_total,
            'used': mem_used,
            'percent': mem_percent
        },
        'disk': {
            'total': disk_total,
            'used': disk_used,
            'percent': disk_percent
        },
        'network': {
            'sent': net_sent,
            'recv': net_recv
        },
        'system': {
            'boot_time': boot_time,
            'info': system_info
        },
        'processes': processes,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


@main_bp.route('/status')
def status():
    return render_template('status.html')


@main_bp.route('/api/system_info')
def system_info():
    return jsonify(get_system_info())

@main_bp.route('/knowledge')
def knowledge_graph():
    """知识图谱可视化页面"""
    # 获取一些基础数据用于下拉菜单
    rivers = River.query.order_by(River.name).all()
    basins = Basin.query.order_by(Basin.name).all()
    facilities = FloodControlFacility.query.order_by(FloodControlFacility.name).all()

    return render_template('knowledge_graph.html',
                           rivers=rivers,
                           basins=basins,
                           facilities=facilities)
@main_bp.route('/debug/routes')
def debug_routes():
    """显示所有已注册的路由信息（调试用）"""
    routes = []
    for rule in current_app.url_map.iter_rules():
        if not rule.endpoint.startswith('static'):  # 过滤掉静态文件路由
            routes.append({
                'endpoint': rule.endpoint,
                'methods': sorted(rule.methods),
                'path': str(rule)
            })
    return jsonify(sorted(routes, key=lambda x: x['endpoint']))