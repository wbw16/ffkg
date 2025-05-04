from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import (
    Basin, River, Reservoir,
    FloodControlFacility, WeatherStation, MonitoringStation
)
from app.extensions import db
from datetime import datetime, timedelta

# ==================== 蓝图注册 ====================


monitors_bp = Blueprint('monitor', __name__, url_prefix='/monitors')


# ==================== 辅助函数 ====================
def get_related_objects():
    """获取关联对象用于表单选择"""
    return {
        'basins': Basin.query.all(),
        'rivers': River.query.all(),
        'reservoirs': Reservoir.query.all()
    }


# ==================== 监测站路由 ====================
@monitors_bp.route('/')
def list_monitors():
    monitors = MonitoringStation.query.outerjoin(River).outerjoin(Reservoir).all()
    return render_template('monitors/list.html', monitors=monitors)


@monitors_bp.route('/create', methods=['GET', 'POST'])
def create_monitor():
    if request.method == 'POST':
        try:
            monitor = MonitoringStation(
                monitor_id=request.form['monitor_id'],
                name=request.form['name'],
                type=request.form['type'],
                river_id=int(request.form['river_id']) if request.form['river_id'] else None,
                reservoir_id=int(request.form['reservoir_id']) if request.form['reservoir_id'] else None
            )
            db.session.add(monitor)
            db.session.commit()
            flash('监测站创建成功', 'success')
            return redirect(url_for('monitor.list_monitors'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败: {str(e)}', 'error')

    related = get_related_objects()
    return render_template('monitors/create.html', **related)


# 在monitors_bp蓝图下添加编辑和删除路由
@monitors_bp.route('/<int:monitor_id>/edit', methods=['GET', 'POST'])
def edit_monitor(monitor_id):
    monitor = MonitoringStation.query.get_or_404(monitor_id)
    if request.method == 'POST':
        try:
            monitor.name = request.form['name']
            monitor.type = request.form['type']
            monitor.river_id = int(request.form['river_id']) if request.form['river_id'] else None
            monitor.reservoir_id = int(request.form['reservoir_id']) if request.form['reservoir_id'] else None
            db.session.commit()
            flash('监测站更新成功', 'success')
            return redirect(url_for('monitor.list_monitors'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'error')

    related = get_related_objects()
    return render_template('monitors/edit.html', monitor=monitor, **related)


@monitors_bp.route('/<int:monitor_id>/delete', methods=['POST'])
def delete_monitor(monitor_id):
    monitor = MonitoringStation.query.get_or_404(monitor_id)
    try:
        db.session.delete(monitor)
        db.session.commit()
        flash('监测站删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'error')
    return redirect(url_for('monitor.list_monitors'))
