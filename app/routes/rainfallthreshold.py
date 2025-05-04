from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import db, RainfallThreshold, Basin
from app.forms import RainfallThresholdForm
from datetime import datetime

rainfall_threshold_bp = Blueprint('rainfall_threshold', __name__, url_prefix='/rainfall-thresholds')


@rainfall_threshold_bp.route('/')
def list_thresholds():
    page = request.args.get('page', 1, type=int)
    basin_id = request.args.get('basin_id', type=int)

    query = RainfallThreshold.query.order_by(RainfallThreshold.threshold_id.desc())

    if basin_id:
        query = query.filter_by(basin_id=basin_id)

    thresholds = query.paginate(page=page, per_page=20)
    basins = Basin.query.order_by(Basin.name).all()

    return render_template('rainfall_thresholds/list.html',
                           thresholds=thresholds,
                           basins=basins,
                           current_basin_id=basin_id)


@rainfall_threshold_bp.route('/create', methods=['GET', 'POST'])
 
def create_threshold():
    form = RainfallThresholdForm()

    if form.validate_on_submit():
        try:
            threshold = RainfallThreshold(
                basin_id=form.basin_id.data,
                threshold_value=form.threshold_value.data,
                description=form.description.data
            )
            db.session.add(threshold)
            db.session.commit()
            flash('降雨量阈值已创建成功', 'success')
            return redirect(url_for('rainfall_threshold.list_thresholds'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败: {str(e)}', 'danger')

    return render_template('rainfall_thresholds/create.html', form=form)


@rainfall_threshold_bp.route('/<int:threshold_id>/edit', methods=['GET', 'POST'])
 
def edit_threshold(threshold_id):
    threshold = RainfallThreshold.query.get_or_404(threshold_id)
    form = RainfallThresholdForm(obj=threshold)

    if form.validate_on_submit():
        try:
            form.populate_obj(threshold)
            db.session.commit()
            flash('降雨量阈值已更新', 'success')
            return redirect(url_for('rainfall_threshold.list_thresholds'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')

    return render_template('rainfall_thresholds/edit.html',
                           form=form,
                           threshold=threshold)


@rainfall_threshold_bp.route('/<int:threshold_id>/delete', methods=['POST'])
 
def delete_threshold(threshold_id):
    threshold = RainfallThreshold.query.get_or_404(threshold_id)
    try:
        db.session.delete(threshold)
        db.session.commit()
        flash('降雨量阈值已删除', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'danger')

    return redirect(url_for('rainfall_threshold.list_thresholds'))
