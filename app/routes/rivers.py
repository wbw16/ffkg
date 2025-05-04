from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import (
    Basin, River, Reservoir,
    FloodControlFacility, WeatherStation, MonitoringStation
)
from app.extensions import db
from datetime import datetime, timedelta

rivers_bp = Blueprint('river', __name__, url_prefix='/rivers')

# ==================== 辅助函数 ====================
def get_related_objects():
    """获取关联对象用于表单选择"""
    return {
        'basins': Basin.query.all(),
        'rivers': River.query.all(),
        'reservoirs': Reservoir.query.all()
    }
# ==================== 河流路由 ====================
@rivers_bp.route('/')
def list_rivers():
    rivers = River.query.join(Basin).order_by(River.river_id).all()
    return render_template('rivers/list.html', rivers=rivers)


@rivers_bp.route('/create', methods=['GET', 'POST'])
def create_river():
    if request.method == 'POST':
        try:
            river = River(
                river_id=request.form['river_id'],
                name=request.form['name'],
                length=float(request.form['length']),
                basin_id=int(request.form['basin_id'])
            )
            db.session.add(river)
            db.session.commit()
            flash('河流创建成功', 'success')
            return redirect(url_for('river.list_rivers'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败: {str(e)}', 'error')

    related = get_related_objects()
    return render_template('rivers/create.html', **related)


@rivers_bp.route('/<int:river_id>/edit', methods=['GET', 'POST'])
def edit_river(river_id):
    river = River.query.get_or_404(river_id)
    if request.method == 'POST':
        try:
            river.name = request.form['name']
            river.length = float(request.form['length'])
            river.basin_id = int(request.form['basin_id'])
            db.session.commit()
            flash('河流更新成功', 'success')
            return redirect(url_for('river.list_rivers'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'error')

    related = get_related_objects()
    return render_template('rivers/edit.html', river=river, **related)


@rivers_bp.route('/<int:river_id>/delete', methods=['POST'])
def delete_river(river_id):
    river = River.query.get_or_404(river_id)
    try:
        db.session.delete(river)
        db.session.commit()
        flash('河流删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'error')
    return redirect(url_for('river.list_rivers'))
