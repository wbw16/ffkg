from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import (
    Basin, River, Reservoir,
    FloodControlFacility, WeatherStation, MonitoringStation
)
from app.extensions import db
from datetime import datetime, timedelta

# ==================== 蓝图注册 ====================

stations_bp = Blueprint('station', __name__, url_prefix='/stations')

# ==================== 辅助函数 ====================
def get_related_objects():
    """获取关联对象用于表单选择"""
    return {
        'basins': Basin.query.all(),
        'rivers': River.query.all(),
        'reservoirs': Reservoir.query.all()
    }

# ==================== 气象站路由 ====================
@stations_bp.route('/')
def list_stations():
    stations = WeatherStation.query.join(Basin).order_by(WeatherStation.station_id).all()
    return render_template('stations/list.html', stations=stations)


@stations_bp.route('/create', methods=['GET', 'POST'])
def create_station():
    if request.method == 'POST':
        try:
            station = WeatherStation(
                station_id=request.form['station_id'],
                name=request.form['name'],
                latitude=float(request.form['latitude']),
                longitude=float(request.form['longitude']),
                basin_id=int(request.form['basin_id'])
            )
            db.session.add(station)
            db.session.commit()
            flash('气象站创建成功', 'success')
            return redirect(url_for('station.list_stations'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败: {str(e)}', 'error')

    related = get_related_objects()
    return render_template('stations/create.html', **related)


# 在stations_bp蓝图下添加编辑和删除路由
@stations_bp.route('/<int:station_id>/edit', methods=['GET', 'POST'])
def edit_station(station_id):
    station = WeatherStation.query.get_or_404(station_id)
    if request.method == 'POST':
        try:
            station.name = request.form['name']
            station.latitude = float(request.form['latitude'])
            station.longitude = float(request.form['longitude'])
            station.basin_id = int(request.form['basin_id'])
            db.session.commit()
            flash('气象站更新成功', 'success')
            return redirect(url_for('station.list_stations'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'error')

    related = get_related_objects()
    return render_template('stations/edit.html', station=station, **related)


@stations_bp.route('/<int:station_id>/delete', methods=['POST'])
def delete_station(station_id):
    station = WeatherStation.query.get_or_404(station_id)
    try:
        db.session.delete(station)
        db.session.commit()
        flash('气象站删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'error')
    return redirect(url_for('station.list_stations'))

