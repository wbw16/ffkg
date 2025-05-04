from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import db, WaterLevelThreshold, River
from app.forms import WaterLevelThresholdForm

water_level_threshold_bp = Blueprint('water_level_threshold', __name__, url_prefix='/water-level-thresholds')


@water_level_threshold_bp.route('/')
def list_thresholds():
    page = request.args.get('page', 1, type=int)
    river_id = request.args.get('river_id', type=int)

    query = WaterLevelThreshold.query.order_by(WaterLevelThreshold.threshold_id.desc())

    if river_id:
        query = query.filter_by(river_id=river_id)

    thresholds = query.paginate(page=page, per_page=20)
    rivers = River.query.order_by(River.name).all()

    return render_template('water_level_thresholds/list.html',
                           thresholds=thresholds,
                           rivers=rivers,
                           current_river_id=river_id)


@water_level_threshold_bp.route('/create', methods=['GET', 'POST'])
 
def create_threshold():
    form = WaterLevelThresholdForm()

    if form.validate_on_submit():
        try:
            threshold = WaterLevelThreshold(
                river_id=form.river_id.data,
                threshold_value=form.threshold_value.data,
                description=form.description.data
            )
            db.session.add(threshold)
            db.session.commit()
            flash('水位阈值已创建成功', 'success')
            return redirect(url_for('water_level_threshold.list_thresholds'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败: {str(e)}', 'danger')

    return render_template('water_level_thresholds/create.html', form=form)


@water_level_threshold_bp.route('/<int:threshold_id>/edit', methods=['GET', 'POST'])
 
def edit_threshold(threshold_id):
    threshold = WaterLevelThreshold.query.get_or_404(threshold_id)
    form = WaterLevelThresholdForm(obj=threshold)

    if form.validate_on_submit():
        try:
            form.populate_obj(threshold)
            db.session.commit()
            flash('水位阈值已更新', 'success')
            return redirect(url_for('water_level_threshold.list_thresholds'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')

    return render_template('water_level_thresholds/edit.html',
                           form=form,
                           threshold=threshold)


@water_level_threshold_bp.route('/<int:threshold_id>/delete', methods=['POST'])
 
def delete_threshold(threshold_id):
    threshold = WaterLevelThreshold.query.get_or_404(threshold_id)
    try:
        db.session.delete(threshold)
        db.session.commit()
        flash('水位阈值已删除', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'danger')

    return redirect(url_for('water_level_threshold.list_thresholds'))
