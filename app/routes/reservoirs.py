from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import (
    Basin, River, Reservoir,
    FloodControlFacility, WeatherStation, MonitoringStation
)
from app.extensions import db
from datetime import datetime, timedelta

# ==================== 蓝图注册 ====================

reservoirs_bp = Blueprint('reservoir', __name__, url_prefix='/reservoirs')

def get_related_objects():
    """获取关联对象用于表单选择"""
    return {
        'basins': Basin.query.all(),
        'rivers': River.query.all(),
        'reservoirs': Reservoir.query.all()
    }


# ==================== 水库路由 ====================
@reservoirs_bp.route('/')
def list_reservoirs():
    reservoirs = Reservoir.query.join(River).order_by(Reservoir.reservoir_id).all()
    return render_template('reservoirs/list.html', reservoirs=reservoirs)


@reservoirs_bp.route('/create', methods=['GET', 'POST'])
def create_reservoir():
    if request.method == 'POST':
        try:
            reservoir = Reservoir(
                reservoir_id=request.form['reservoir_id'],
                name=request.form['name'],
                capacity=float(request.form['capacity']),
                river_id=int(request.form['river_id'])
            )
            db.session.add(reservoir)
            db.session.commit()
            flash('水库创建成功', 'success')
            return redirect(url_for('reservoir.list_reservoirs'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败: {str(e)}', 'error')

    related = get_related_objects()
    return render_template('reservoirs/create.html', **related)


@reservoirs_bp.route('/<int:reservoir_id>/edit', methods=['GET', 'POST'])
def edit_reservoir(reservoir_id):
    reservoir = Reservoir.query.get_or_404(reservoir_id)
    if request.method == 'POST':
        try:
            reservoir.name = request.form['name']
            reservoir.capacity = float(request.form['capacity'])
            reservoir.river_id = int(request.form['river_id'])
            db.session.commit()
            flash('水库更新成功', 'success')
            return redirect(url_for('reservoir.list_reservoirs'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'error')

    related = get_related_objects()
    return render_template('reservoirs/edit.html', reservoir=reservoir, **related)

# 在reservoirs_bp蓝图下添加删除路由
@reservoirs_bp.route('/<int:reservoir_id>/delete', methods=['POST'])
def delete_reservoir(reservoir_id):
    reservoir = Reservoir.query.get_or_404(reservoir_id)
    try:
        db.session.delete(reservoir)
        db.session.commit()
        flash('水库删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'error')
    return redirect(url_for('reservoir.list_reservoirs'))
