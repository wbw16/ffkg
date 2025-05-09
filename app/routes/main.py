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

@main_bp.route('/about')
def about():
    return render_template('about.html')

