from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models import db
from app.forms import ThresholdForm
from datetime import datetime

threshold_bp = Blueprint('threshold', __name__, url_prefix='/thresholds')


@threshold_bp.route('/')
def list_thresholds():
    # 从子类获取具体模型（假设为WaterThreshold）
    model = get_threshold_model()
    thresholds = model.query.order_by(model.threshold_id.desc()).all()
    return render_template('thresholds/list.html',
                           thresholds=thresholds,
                           model_name=model.__name__)


@threshold_bp.route('/create', methods=['GET', 'POST'])
 
def create_threshold():
    form = ThresholdForm()

    if form.validate_on_submit():
        try:
            model = get_threshold_model()
            threshold = model(
                threshold_value=form.threshold_value.data,
                description=form.description.data
            )
            db.session.add(threshold)
            db.session.commit()
            flash('阈值已成功创建', 'success')
            return redirect(url_for('threshold.list_thresholds'))
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败: {str(e)}', 'danger')

    return render_template('thresholds/create.html',
                           form=form,
                           model_name=get_threshold_model().__name__)


@threshold_bp.route('/<int:threshold_id>/edit', methods=['GET', 'POST'])
 
def edit_threshold(threshold_id):
    model = get_threshold_model()
    threshold = model.query.get_or_404(threshold_id)
    form = ThresholdForm(obj=threshold)

    if form.validate_on_submit():
        try:
            form.populate_obj(threshold)
            db.session.commit()
            flash('阈值已更新', 'success')
            return redirect(url_for('threshold.list_thresholds'))
        except Exception as e:
            db.session.rollback()
            flash(f'更新失败: {str(e)}', 'danger')

    return render_template('thresholds/edit.html',
                           form=form,
                           threshold=threshold,
                           model_name=model.__name__)


@threshold_bp.route('/<int:threshold_id>/delete', methods=['POST'])
 
def delete_threshold(threshold_id):
    model = get_threshold_model()
    threshold = model.query.get_or_404(threshold_id)
    try:
        db.session.delete(threshold)
        db.session.commit()
        flash('阈值已删除', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'danger')

    return redirect(url_for('threshold.list_thresholds'))


def get_threshold_model():
    """动态获取当前使用的阈值模型"""
    from app.models import ThresholdBase  # 示例模型
    return ThresholdBase
