from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import HistoricalFloodData, River
from app.forms import HistoricalFloodForm
from app.extensions import db
from datetime import datetime

flood_bp = Blueprint('historical_flood', __name__, url_prefix='/historical-floods')


@flood_bp.route('/')
def list_floods():
    # 获取查询参数
    river_id = request.args.get('river_id', type=int)
    page = request.args.get('page', 1, type=int)

    # 构建查询
    query = HistoricalFloodData.query.order_by(HistoricalFloodData.start_time.desc())

    if river_id:
        query = query.filter_by(river_id=river_id)

    floods = query.paginate(page=page, per_page=20)
    rivers = River.query.order_by(River.name).all()

    return render_template('historical_floods/list.html',
                           floods=floods,
                           rivers=rivers,
                           current_river_id=river_id)


@flood_bp.route('/create', methods=['GET', 'POST'])
 
def create_flood():
    form = HistoricalFloodForm()

    if form.validate_on_submit():
        try:
            flood = HistoricalFloodData(
                river_id=form.river_id.data,
                start_time=form.start_time.data,
                end_time=form.end_time.data,
                max_water_level=form.max_water_level.data,
                affected_area=form.affected_area.data
            )
            db.session.add(flood)
            db.session.commit()
            flash('历史洪水记录已成功创建', 'success')
            return redirect(url_for('historical_flood.list_floods'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败: {str(e)}', 'danger')

    return render_template('historical_floods/create.html', form=form)


@flood_bp.route('/<int:flood_id>/edit', methods=['GET', 'POST'])
 
def edit_flood(flood_id):
    flood = HistoricalFloodData.query.get_or_404(flood_id)
    form = HistoricalFloodForm(obj=flood)

    if form.validate_on_submit():
        try:
            form.populate_obj(flood)
            db.session.commit()
            flash('历史洪水记录已更新', 'success')
            return redirect(url_for('historical_flood.list_floods'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')

    return render_template('historical_floods/edit.html', form=form, flood=flood)


@flood_bp.route('/<int:flood_id>/delete', methods=['POST'])
 
def delete_flood(flood_id):
    flood = HistoricalFloodData.query.get_or_404(flood_id)
    try:
        db.session.delete(flood)
        db.session.commit()
        flash('历史洪水记录已删除', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'danger')

    return redirect(url_for('historical_flood.list_floods'))
