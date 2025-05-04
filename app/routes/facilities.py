from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import (
    Basin, River, Reservoir,
    FloodControlFacility, WeatherStation, MonitoringStation
)
from app.extensions import db
from datetime import datetime, timedelta

# ==================== 蓝图注册 ====================
facilities_bp = Blueprint('facility', __name__, url_prefix='/facilities')

# ==================== 辅助函数 ====================
def get_related_objects():
    """获取关联对象用于表单选择"""
    return {
        'basins': Basin.query.all(),
        'rivers': River.query.all(),
        'reservoirs': Reservoir.query.all()
    }

# ==================== 防洪设施路由 ====================
@facilities_bp.route('/')
def list_facilities():
    facilities = FloodControlFacility.query.join(River).order_by(FloodControlFacility.facility_id).all()
    return render_template('facilities/list.html', facilities=facilities)


@facilities_bp.route('/create', methods=['GET', 'POST'])
def create_facility():
    if request.method == 'POST':
        try:
            facility = FloodControlFacility(
                facility_id=request.form['facility_id'],
                name=request.form['name'],
                type=request.form['type'],
                river_id=int(request.form['river_id'])
            )
            db.session.add(facility)
            db.session.commit()
            flash('防洪设施创建成功', 'success')
            return redirect(url_for('facility.list_facilities'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败: {str(e)}', 'error')

    related = get_related_objects()
    return render_template('facilities/create.html', **related)


# 在facilities_bp蓝图下添加以下路由
@facilities_bp.route('/<int:facility_id>/edit', methods=['GET', 'POST'])
def edit_facility(facility_id):
    facility = FloodControlFacility.query.get_or_404(facility_id)
    if request.method == 'POST':
        try:
            facility.name = request.form['name']
            facility.type = request.form['type']
            facility.river_id = int(request.form['river_id'])
            db.session.commit()
            flash('防洪设施更新成功', 'success')
            return redirect(url_for('facility.list_facilities'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'error')

    related = get_related_objects()
    return render_template('facilities/edit.html', facility=facility, **related)


@facilities_bp.route('/<int:facility_id>/delete', methods=['POST'])
def delete_facility(facility_id):
    facility = FloodControlFacility.query.get_or_404(facility_id)
    try:
        db.session.delete(facility)
        db.session.commit()
        flash('防洪设施删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'error')
    return redirect(url_for('facility.list_facilities'))

