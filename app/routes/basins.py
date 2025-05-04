from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import (
    Basin, River, Reservoir,
    FloodControlFacility, WeatherStation, MonitoringStation
)
from app.extensions import db
from datetime import datetime, timedelta

def get_related_objects():
    """获取关联对象用于表单选择"""
    return {
        'basins': Basin.query.all(),
        'rivers': River.query.all(),
        'reservoirs': Reservoir.query.all()
    }

basins_bp = Blueprint('basin', __name__, url_prefix='/basins')
# ==================== 流域路由 ====================
@basins_bp.route('/')
def list_basins():
    basins = Basin.query.order_by(Basin.basin_id).all()
    return render_template('basins/list.html', basins=basins)


@basins_bp.route('/create', methods=['GET', 'POST'])
def create_basin():
    if request.method == 'POST':
        try:
            basin = Basin(
                basin_id=request.form['basin_id'],
                name=request.form['name'],
                area=float(request.form['area']),
                region=request.form['region']
            )
            db.session.add(basin)
            db.session.commit()
            flash('流域创建成功', 'success')
            return redirect(url_for('basin.list_basins'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败: {str(e)}', 'error')
    return render_template('basins/create.html')


@basins_bp.route('/<int:basin_id>/edit', methods=['GET', 'POST'])
def edit_basin(basin_id):
    basin = Basin.query.get_or_404(basin_id)
    if request.method == 'POST':
        try:
            basin.name = request.form['name']
            basin.area = float(request.form['area'])
            basin.region = request.form['region']
            db.session.commit()
            flash('流域更新成功', 'success')
            return redirect(url_for('basin.list_basins'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'error')
    return render_template('basins/edit.html', basin=basin)


@basins_bp.route('/<int:basin_id>/delete', methods=['POST'])
def delete_basin(basin_id):
    basin = Basin.query.get_or_404(basin_id)
    try:
        db.session.delete(basin)
        db.session.commit()
        flash('流域删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'error')
    return redirect(url_for('basin.list_basins'))
